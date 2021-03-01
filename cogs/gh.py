"""Name, credits, license, and general overview of file"""

# Lib
from functools import wraps
from typing import Optional
from urllib.parse import quote

# Site
from discord.colour import Colour
from discord.ext.commands.cog import Cog
from discord.ext.commands.context import Context
from discord.ext.commands.core import group
from discord.utils import get
from github import NamedUser
from github.MainClass import Github
from github.GithubException import BadCredentialsException

# Local
from utils.classes import Bot, Embed, SubRedis


class Emojis:

    def __init__(self, bot: Bot):

        def check(attr):
            return not attr.startswith("__") and isinstance(getattr(self, attr), str)
        self.__slots__ = attrs = [attr for attr in dir(self) if check(attr)]
        emojis = bot.emojis

        for attr in attrs:
            emoji = get(emojis, name=attr)
            if emoji:
                setattr(self, attr, emoji)
            else:
                setattr(self, attr, getattr(Emojis, attr))

    def __len__(self):
        return len(self.__slots__)

    def __getitem__(self, item: str):
        return getattr(self, item)

    def __iter__(self):
        for item in self.__slots__:
            yield getattr(self, item)

    def items(self):
        return {key: getattr(self, key) for key in self.__slots__}.items()

    def keys(self):
        return self.__slots__

    def values(self):
        return list(self)

    gitrepo = b"\xF0\x9F\x93\x92".decode()                 # 📒  :ledger:
    gitbranch = b"\xE2\xB4\xB5\xEF\xB8\x8F".decode()       # ⤵️:arrow_heading_down:
    gitfork = b"\xF0\x9F\x94\x80".decode()                 # 🔀   :twisted_rightwards_arrows:
    gitcommit = b"\xE2\x86\x97\xEF\xB8\x8F".decode()       # ↗️:arrow_upper_right:
    gitcompare = b"\xE2\x86\x94\xEF\xB8\x8F".decode()      # ↔️:left_right_arrow:
    gitmerge = b"\xF0\x9F\x94\x81".decode()                # 🔁   :repeat:
    gitpullrequest = b"\xE2\xA4\xB4\xEF\xB8\x8F".decode()  # ⤴️:arrow_heading_up:
    gitgist = b"\xF0\x9F\x93\x84".decode()                 # 📄  :page_facing_up:
    gitcode = b"\xF0\x9F\x93\x9D".decode()                 # 📝  :memo:
    gitstar = b"\xE2\xAD\x90".decode()                     # ⭐  :star:
    gitwatch = b"\xF0\x9F\x91\x81\xEF\xB8\x8F".decode()    # 👁️  :eye:
    gitissue = b"\xF0\x9F\x95\xB7\xEF\xB8\x8F".decode()    # 🕷️  :spider:


def is_authed(func):

    @wraps(func)
    async def wrapper(self, ctx: Context, *args, **kwargs):

        if self.gh_client:
            await func(self, ctx, *args, **kwargs)

        else:
            await self.bot.send_help_for(
                ctx, self.bot.get_command("gh auth"),
                "GitHub Application Token missing or invalid.\n"
                "Replace token in database and try re-authenticating."
            )

    return wrapper


class GitHub(Cog):
    """GitHub"""

    def __init__(self, bot: Bot):

        self.bot = bot
        self.config = SubRedis(bot.db, "github")
        self.emojis = Emojis(bot)

        self.errorlog = bot.errorlog

        self.gh_client = self.try_auth()

        self.__cache = {
            "user": dict(),
            "repo": dict()
        }

        if self.gh_client:
            self._user = self.user = self.gh_client.get_user()
            self._repo = self.repo = self.user.get_repo(self.bot.APP_NAME)

    async def cog_check(self, ctx: Context) -> bool:
        return await self.bot.is_owner(ctx.author)

    def try_auth(self) -> Optional[Github]:
        """Create Github client object and attempt hitting API with token"""

        token = self.config.get("token")

        if token:
            try:
                gh_client = Github(token)
                _ = gh_client.get_rate_limit()
                return gh_client

            except BadCredentialsException:
                return None

    async def get_user(self, ctx: Context, name: str = None) -> Optional[NamedUser]:
        try:
            if name == "self":
                user = self._user

            elif name:
                user = self.gh_client.get_user(name)

            else:
                user = self.user

            self.__cache["user"]["repos"] = list(user.get_repos())
            self.__cache["user"]["gists"] = list(user.get_gists())
            self.__cache["user"]["stars"] = list(user.get_starred())

        except Exception as e:
            self.__cache["user"] = dict()
            self.__cache["repo"] = dict()

            await self.errorlog.send(e, ctx)

    @group(name="gh", invoke_without_command=True)
    @is_authed
    async def gh(self, ctx: Context):
        """GitHub

        Something"""
        user = f"[{self.user.name}]({self.user.html_url})" if self.user else "None Selected"
        repo = f"[{self.repo.name}]({self.repo.html_url})" if self.repo else "None Selected"

        msg = f"**__Current Selections:__**\n" \
              f"__User:__ {user}\n" \
              f"__Repository:__ {repo}"

        await self.bot.send_help_for(ctx, ctx.command, msg)

    @gh.command(name="auth")
    async def auth(self, ctx: Context):
        """Authenticate With GitHub Token

        Something something"""
        pass

    @gh.command(name="user")
    async def user(self, ctx: Context, *, user: str = None):
        """GitHub User

        Selects a GitHub user account and shows a brief of the profile.
        `[p]gh user <username>` will select a user account
        `[p]gh user self` will select your user account
        `[p]gh user` will display the currently selected user"""

        self.user = user = await self.get_user(ctx, user)

        if user:

            if self.repo.owner.name != self.user.name:
                self.repo = None

            repos = self.__cache["user"]["repos"]
            gists = self.__cache["user"]["gists"]
            stars = self.__cache["user"]["stars"]

            repos_url = quote(f"{user.html_url}?tab=repositories")
            gists_url = quote(f"https://gist.github.com/{user.login}")
            stars_url = quote(f"{user.html_url}?tab=stars")

            em = Embed(
                title=f"{user.login}'s Public GitHub Profile",
                description=f"*\"{user.bio}\"*\n\n"
                            f"{self.emojis.gitrepo} [Repositories]({repos_url}): {len(repos)}\n"
                            f"{self.emojis.gitgist} [Gists]({gists_url}): {len(gists)}\n"
                            f"{self.emojis.gitstar} [Starred Repositories]({stars_url}): {len(stars)}",
                color=Colour.green()
            )
            em.set_author(name=user.name, url=user.html_url, icon_url=user.avatar_url)

        else:
            self.__cache["user"] = dict()
            self.__cache["repo"] = dict()

            em = Embed(
                title="GitHub: Error",
                description="Unable to load user or user not found",
                color=Colour.red()
            )

        await ctx.send(embed=em)

    @gh.command(name="repo")
    async def repo(self, ctx: Context, *, repo: str = None):
        """User

        Selects a GitHub user account and shows a brief of the profile.
        `[p]gh user <username>` will select a user account
        `[p]gh user self` will select your user account
        `[p]gh user` will display the currently selected user"""

        try:
            if repo == "self":
                self.user = user = self._user
                self.repo = repo = self._repo

            elif repo:
                user = self.user
                self.repo = repo = user.get_repo(repo)

            else:
                if self.user:
                    user = self.user

                else:
                    return await self.bot.send_help_for(
                        ctx, ctx.command,
                        "No user is currently selected."
                    )

                if self.repo:
                    repo = self.repo

                else:
                    return await self.bot.send_help_for(
                        ctx, ctx.command,
                        "No repo is currently selected."
                    )

            self.__cache["repo"]["branches"] = branches = list(repo.get_branches())
            self.__cache["repo"]["stars"] = stars = list(repo.get_stargazers())
            self.__cache["repo"]["forks"] = forks = list(repo.get_forks())
            self.__cache["repo"]["watchers"] = watchers = list(repo.get_watchers())
            self.__cache["repo"]["issues"] = issues = list(repo.get_issues(state="open"))

            em = Embed(
                title=f"[{repo.full_name}]({repo.html_url})",
                description=f"{self.emojis.gitbranch} [Branches]({repo.html_url}/branches): {len(branches)}\n"
                            f"{self.emojis.gitstar} [Stars]({repo.html_url}/stargazers): {len(stars)}\n"
                            f"{self.emojis.gitfork} [Forks]({repo.html_url}/network/members): {len(forks)}\n"
                            f"{self.emojis.gitwatch} [Watchers]({repo.html_url}/watchers): {len(watchers)}\n\n"
                            f"{self.emojis.gitissue} [Open Issues]({repo.html_url}/issues): {len(issues)}\n",
                color=Colour.green()
            )
            em.set_author(name=user.login, url=user.html_url, icon_url=user.avatar_url)

        except:
            self.repo = None
            em = Embed(
                title="GitHub: Error",
                description="Unable to load repo or repo not found",
                color=Colour.red()
            )

        await ctx.send(embed=em)

    @gh.group(name="issues", invoke_without_command=True, aliases=["issue"])
    async def issues(self, ctx: Context, state: str = "all"):
        """Issues

        View and manage issues on a repo"""

        state = state.lower()
        if state not in ("open", "closed", "all"):
            return await self.bot.send_help_for(ctx.command, "Valid states: `open`, `closed`, `all`")

        em = Embed()

        for issue in self.repo.get_issues(state=state):
            pass


def setup(bot: Bot):
    """GitHub"""
    bot.add_cog(GitHub(bot))
