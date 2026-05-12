import asyncio
import json
import logging
import os

import discord
from core.classes import Cog_Extension
from discord.ext import commands

import engine
from engine import session_store

logger = logging.getLogger(__name__)

_AUTHOR_NAME = "Made by: oceansfavor"
_AUTHOR_URL = "https://www.instagram.com/oceansfavor/"
_AUTHOR_ICON = "https://i.imgur.com/tax7zpT.jpg"
_COLOR = 0xEDF10E
_WIN_COLOR = 0x2ECC71

_PROGRESS_PHASES = [
    (15, "🎲 正在生成你的逃脫場景... 設計房間中"),
    (15, "🎲 正在生成你的逃脫場景... 安排謎題中"),
    (15, "🎲 正在生成你的逃脫場景... 即將完成"),
    (15, "🎲 場景比較複雜，再等一下..."),
]


class Escape(Cog_Extension):

    def __init__(self, bot):
        super().__init__(bot)
        # In-memory set of usernames with an active (unpaused) session.
        # Cleared on bot restart; users resume with `escape L`.
        self._active_sessions: set[str] = set()

    # ── Embed helpers ───────────────────────────────────────────────────────

    def _narration_embed(self, world_state, narration: str, username: str) -> discord.Embed:
        loc = world_state.locations.get(world_state.current_location_id)
        loc_name = loc.name if loc else "???"
        embed = discord.Embed(title=loc_name, description=narration, color=_COLOR)
        embed.set_author(name=_AUTHOR_NAME, url=_AUTHOR_URL, icon_url=_AUTHOR_ICON)

        inv_names = [world_state.items[i].name for i in world_state.inventory if i in world_state.items]
        if inv_names:
            embed.add_field(name="Inventory", value=", ".join(inv_names), inline=False)

        embed.set_footer(text=f"{username} is playing! · Turn {world_state.turn_count}")
        return embed

    def _win_embed(self, world_state, username: str) -> discord.Embed:
        embed = discord.Embed(
            title="🎉 你逃出去了！",
            description=(
                f"**{username}** 成功逃脫！\n\n"
                f"共用了 **{world_state.turn_count}** 回合。\n\n"
                "Type `escape N` to play again."
            ),
            color=_WIN_COLOR,
        )
        embed.set_author(name=_AUTHOR_NAME, url=_AUTHOR_URL, icon_url=_AUTHOR_ICON)
        return embed

    def _text_embed(self, title: str, description: str) -> discord.Embed:
        embed = discord.Embed(title=title, description=description, color=_COLOR)
        embed.set_author(name=_AUTHOR_NAME, url=_AUTHOR_URL, icon_url=_AUTHOR_ICON)
        return embed

    # ── User registry (legacy compat) ───────────────────────────────────────

    def _register_user(self, username: str) -> None:
        path = "User/userlist.json"
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            data = {"users": []}
        if username not in data["users"]:
            data["users"].append(username)
        os.makedirs("User", exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)

    # ── Progress updater ────────────────────────────────────────────────────

    @staticmethod
    async def _run_progress_updates(msg: discord.Message) -> None:
        """Edit msg through generation progress phases until cancelled."""
        try:
            for delay, text in _PROGRESS_PHASES:
                await asyncio.sleep(delay)
                await msg.edit(content=text)
        except asyncio.CancelledError:
            pass

    # ── Commands ────────────────────────────────────────────────────────────

    @commands.group(brief='call escape game')
    async def escape(self, ctx) -> None:
        if ctx.invoked_subcommand is None:
            await ctx.send('Enter "escape H" to check how to play.')

    @escape.command(brief='new game, "escape N"')
    async def N(self, ctx) -> None:
        user = ctx.author.name

        # Immediate visual feedback — edit this message in-place throughout generation.
        status_msg = await ctx.send("🎲 正在生成你的逃脫場景... (約需 30-60 秒)")

        gen_task = asyncio.create_task(engine.generate(user))
        progress_task = asyncio.create_task(self._run_progress_updates(status_msg))

        try:
            world_state = await gen_task
        except Exception:
            logger.exception("Scenario generation raised unexpectedly for user %s", user)
            progress_task.cancel()
            await status_msg.edit(content="場景生成失敗，請稍後重試 (`escape N`)")
            return

        progress_task.cancel()

        await session_store.save(user, world_state)
        self._register_user(user)
        self._active_sessions.add(user)

        opening = world_state.history[0]["narration"] if world_state.history else "You are in a room. Escape."
        await status_msg.edit(content=None, embed=self._narration_embed(world_state, opening, user))

    @escape.command(brief='resume game, "escape L"')
    async def L(self, ctx) -> None:
        user = ctx.author.name
        world_state = await session_store.load(user)
        if world_state is None:
            await ctx.send("No saved game found. Start a new game with `escape N`.")
            return
        if world_state.is_won:
            await ctx.send("You already escaped! Start a new game with `escape N`.")
            return

        self._active_sessions.add(user)
        last = world_state.history[-1] if world_state.history else None
        last_narration = last["narration"] if last else "You are somewhere in the room."
        resume_text = f"你上次玩到：{last_narration}\n\n繼續玩請輸入任何動作。"
        await ctx.send(embed=self._text_embed("Resuming…", resume_text))

    @escape.command(brief='how to play, "escape H"')
    async def H(self, ctx) -> None:
        embed = self._text_embed(
            "How to Play",
            (
                "Type anything to interact with the world.\n\n"
                "**Examples:** *look around*, *take the notebook*, *go to the corridor*, "
                "*enter 4579*, *inspect the lock*\n\n"
                "Type `q` or `quit` to pause your session (your progress is saved).\n"
                "Type `escape L` to resume.\n"
                "Type `escape N` to start a brand-new game.\n\n"
                "⏳ 場景生成需要 30-60 秒，請耐心等待。"
            ),
        )
        await ctx.send(embed=embed)

    # ── Message listener (free-text game loop) ──────────────────────────────

    @commands.Cog.listener()
    async def on_message(self, msg) -> None:
        if msg.author == self.bot.user:
            return

        # Skip messages that are valid bot commands (escape N/L/H etc.)
        ctx = await self.bot.get_context(msg)
        if ctx.valid:
            return

        user = msg.author.name
        if user not in self._active_sessions:
            return

        txt = msg.content.strip()
        if not txt:
            return

        if txt.lower() in ("q", "quit"):
            self._active_sessions.discard(user)
            await msg.channel.send(
                embed=self._text_embed(
                    "Paused",
                    "Thanks for playing! Your progress is saved. Type `escape L` to resume.",
                )
            )
            return

        world_state = await session_store.load(user)
        if world_state is None or world_state.is_won:
            self._active_sessions.discard(user)
            return

        # Typing indicator covers the 3-8s turn-handler latency.
        async with msg.channel.typing():
            try:
                new_state = await engine.process_turn(world_state, txt)
            except Exception:
                logger.exception("process_turn raised for user %s action %r", user, txt)
                await msg.channel.send("Something went wrong. Try again.")
                return

        await session_store.save(user, new_state)

        last = new_state.history[-1] if new_state.history else {"narration": "Nothing happens."}
        await msg.channel.send(embed=self._narration_embed(new_state, last["narration"], user))

        if new_state.is_won:
            self._active_sessions.discard(user)
            await msg.channel.send(embed=self._win_embed(new_state, user))


async def setup(bot):
    await bot.add_cog(Escape(bot))
