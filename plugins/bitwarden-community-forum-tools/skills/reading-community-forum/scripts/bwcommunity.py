#!/usr/bin/env python3
"""bwcommunity: read-only CLI for the Bitwarden Community forum (Discourse).

Built to be called by Claude via Bash. Standard library only.
Run `bwcommunity --help` or `bwcommunity <command> --help`.
"""

import argparse
import email.utils
import hashlib
import html
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from html.parser import HTMLParser

VERSION = "1.0.0"
DEFAULT_BASE_URL = "https://community.bitwarden.com"
BASE_URL = os.environ.get("BW_COMMUNITY_URL", DEFAULT_BASE_URL).rstrip("/")
UA_TOKEN = "bwcommunity-cli"
_contact = os.environ.get("BW_COMMUNITY_CONTACT")
USER_AGENT = f"{UA_TOKEN}/{VERSION} (read-only research tool" + (f"; contact: {_contact})" if _contact else ")")
CACHE_DIR = os.path.join(os.environ.get("XDG_CACHE_HOME") or os.path.expanduser("~/.cache"), "bwcommunity")
CACHE_TTL = 3600
ROBOTS_TTL = 86400
MIN_INTERVAL = 1.0  # seconds between requests, shared across invocations
MAX_RETRIES = 4
TIMEOUT = 30
CHUNK = 20  # post ids per /t/{id}/posts.json call
RAW_PAGE = 100  # posts per /raw/{topic_id}?page=N
QUOTE_CHARS = 160  # same-thread quotes collapse to this many chars
EXCERPT_CHARS = 220  # list/search snippets
BRIEF_SCAN = 100  # posts --brief looks through for staff/moderator replies
BRIEF_MODS = 3  # volunteer-moderator posts kept by --brief (most liked); staff posts are all kept
HIDDEN_TAGS = {"server:default-cloud"}  # on ~every topic; absence of server:self-hosted already says it

EXIT_OK, EXIT_USAGE, EXIT_NOT_FOUND, EXIT_BLOCKED, EXIT_NETWORK = 0, 1, 2, 3, 4


class CLIError(Exception):
    def __init__(self, message, code):
        super().__init__(message)
        self.code = code


# --------------------------------------------------------------------------- HTTP


class Client:
    def __init__(self, use_cache=True, honour_robots=True, verbose=False):
        self.use_cache = use_cache
        self.honour_robots = honour_robots
        self.verbose = verbose
        self._robots = None
        self.robots_exempt = ()  # path prefixes a command may fetch despite robots.txt
        os.makedirs(CACHE_DIR, mode=0o700, exist_ok=True)
        os.chmod(CACHE_DIR, 0o700)  # makedirs leaves an existing directory's mode alone

    def _log(self, msg):
        if self.verbose:
            print(f"[bwcommunity] {msg}", file=sys.stderr)

    def _headers(self, want_json):
        # Anonymous by design: no credential headers are ever sent, whatever BW_COMMUNITY_URL points at.
        return {"User-Agent": USER_AGENT, "Accept": "application/json" if want_json else "text/plain, */*"}

    def _cache_path(self, url):
        return os.path.join(CACHE_DIR, hashlib.sha256(url.encode()).hexdigest()[:32] + ".cache")

    def _cache_get(self, url, ttl):
        path = self._cache_path(url)
        try:
            if time.time() - os.path.getmtime(path) < ttl:
                with open(path, encoding="utf-8") as f:
                    return f.read()
        except OSError:
            pass
        return None

    def _cache_put(self, url, body):
        path = self._cache_path(url)
        fd = os.open(path + ".tmp", os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(body)
        os.replace(path + ".tmp", path)

    def _throttle(self):
        stamp = os.path.join(CACHE_DIR, ".last_request")
        try:
            wait = MIN_INTERVAL - (time.time() - os.path.getmtime(stamp))
            if wait > 0:
                time.sleep(wait)
        except OSError:
            pass
        with open(stamp, "w"):
            pass
        os.utime(stamp, None)

    def _fetch(self, url, want_json):
        """One GET with retries. Returns body text. Raises CLIError."""
        delay = 2.0
        for attempt in range(MAX_RETRIES + 1):
            self._throttle()
            self._log(f"GET {url}")
            req = urllib.request.Request(url, headers=self._headers(want_json), method="GET")
            try:
                with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
                    body = resp.read().decode("utf-8", errors="replace")
                    ctype = resp.headers.get("Content-Type", "")
                    if want_json and "json" not in ctype:
                        raise CLIError(f"expected JSON from {url}, got {ctype or 'unknown type'} "
                                       "(bot challenge or login wall?)", EXIT_BLOCKED)
                    return body
            except urllib.error.HTTPError as e:
                if e.code == 404:
                    raise CLIError(f"not found (404): {url} (deleted, private or wrong id)", EXIT_NOT_FOUND)
                if e.code in (401, 403):
                    raise CLIError(f"forbidden ({e.code}): {url} (login required or blocked)", EXIT_BLOCKED)
                if e.code == 429 or e.code >= 500:
                    if attempt == MAX_RETRIES:
                        code = EXIT_BLOCKED if e.code == 429 else EXIT_NETWORK
                        raise CLIError(f"HTTP {e.code} after {MAX_RETRIES} retries: {url}", code)
                    wait = _retry_after(e.headers.get("Retry-After")) or delay
                    self._log(f"HTTP {e.code}, retrying in {wait:.0f}s")
                    time.sleep(min(wait, 120))
                    delay *= 2
                    continue
                raise CLIError(f"HTTP {e.code}: {url}", EXIT_NETWORK)
            except (urllib.error.URLError, TimeoutError, ConnectionError) as e:
                if attempt == MAX_RETRIES:
                    raise CLIError(f"network error: {getattr(e, 'reason', e)} ({url})", EXIT_NETWORK)
                self._log(f"network error ({getattr(e, 'reason', e)}), retrying in {delay:.0f}s")
                time.sleep(delay)
                delay *= 2

    def get(self, path, params=None, want_json=True):
        query = urllib.parse.urlencode(params or [], doseq=True)
        path_q = path + ("?" + query if query else "")
        self._check_robots(path_q)
        url = BASE_URL + path_q
        body = self._cache_get(url, CACHE_TTL) if self.use_cache else None
        if body is None:
            body = self._fetch(url, want_json)
            self._cache_put(url, body)
        else:
            self._log(f"cache hit {url}")
        if not want_json:
            return body
        try:
            return json.loads(body)
        except ValueError:
            raise CLIError(f"invalid JSON from {url}", EXIT_NETWORK)

    def _check_robots(self, path_q):
        if not self.honour_robots or path_q.startswith(self.robots_exempt):
            return
        if self._robots is None:
            url = BASE_URL + "/robots.txt"
            text = self._cache_get(url, ROBOTS_TTL)
            if text is None:
                try:
                    text = self._fetch(url, want_json=False)
                except CLIError as e:
                    if e.code != EXIT_NOT_FOUND:
                        raise
                    text = ""
                self._cache_put(url, text)
            self._robots = parse_robots(text, UA_TOKEN)
        rule = robots_disallowed(self._robots, path_q)
        if rule:
            raise CLIError(f"robots.txt disallows {path_q} (rule: Disallow: {rule}). "
                           "Pass --ignore-robots to override.", EXIT_BLOCKED)


def _retry_after(value):
    if not value:
        return None
    try:
        return float(value)
    except ValueError:
        try:
            return max(0.0, email.utils.parsedate_to_datetime(value).timestamp() - time.time())
        except (TypeError, ValueError):
            return None


# ------------------------------------------------------------------------ robots


def parse_robots(text, agent):
    """Return (allow, disallow) rule lists for `agent`, falling back to the `*` group."""
    groups, current, in_rules = {}, [], False
    for line in text.splitlines():
        line = line.split("#", 1)[0].strip()
        if ":" not in line:
            continue
        field, value = (s.strip() for s in line.split(":", 1))
        field = field.lower()
        if field == "user-agent":
            if in_rules:
                current, in_rules = [], False
            current.append(value.lower())
            groups.setdefault(value.lower(), ([], []))
        elif field in ("allow", "disallow") and current:
            in_rules = True
            for ua in current:
                if value:
                    groups[ua][0 if field == "allow" else 1].append(value)
    agent = agent.lower()
    for ua, rules in groups.items():
        if ua != "*" and ua in agent:
            return rules
    return groups.get("*", ([], []))


def _robots_match(rule, path):
    pattern = re.escape(rule).replace(r"\*", ".*")
    if pattern.endswith(r"\$"):
        pattern = pattern[:-2] + "$"
    return re.match(pattern, path) is not None


def robots_disallowed(rules, path):
    """Return the matching Disallow rule if `path` is blocked (longest match wins), else None."""
    allow, disallow = rules
    best_allow = max((len(r) for r in allow if _robots_match(r, path)), default=-1)
    hits = [r for r in disallow if _robots_match(r, path)]
    best = max(hits, key=len, default=None)
    if best is not None and len(best) > best_allow:
        return best
    return None


# ------------------------------------------------------------------- HTML -> text


class _HTMLToMarkdown(HTMLParser):
    BLOCK = {"p", "div", "section", "article", "aside", "header", "footer", "table", "tr", "details", "summary"}

    def __init__(self, base_url, topic_id=None):
        super().__init__(convert_charrefs=True)
        self.base_url = base_url
        self.topic_id = str(topic_id) if topic_id else None  # quotes of this topic get collapsed
        self.out = []
        self.quote_depth = 0
        self.list_stack = []
        self.pre = 0
        self.skip = 0
        self.link = None
        self.at_line_start = True
        self.aside_stack = []  # (kind, start index in out, header) with kind "quote" | "onebox" | ""
        self.bq_stack = []  # True if this <blockquote> raised quote_depth
        self.quote_open = False  # next <blockquote> belongs to an aside.quote

    def _emit(self, text):
        if not text:
            return
        prefix = "> " * self.quote_depth
        lines = text.split("\n")
        for i, line in enumerate(lines):
            if i:
                self.out.append("\n")
                self.at_line_start = True
            if line:
                if self.at_line_start and prefix:
                    self.out.append(prefix)
                self.out.append(line)
                self.at_line_start = False

    def _newline(self, n=1):
        if not self.out:
            return
        tail = "".join(self.out[-4:])
        have = len(tail) - len(tail.rstrip("\n"))
        self.out.extend("\n" * max(0, n - have))
        self.at_line_start = True

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        cls = a.get("class") or ""
        if self.skip:
            if tag in ("div", "span"):
                self.skip += 1
            return
        classes = cls.split()
        if tag in ("div", "span") and ("meta" in classes or "title" in classes and self.aside_stack and self.aside_stack[-1][0].startswith("quote")):
            self.skip = 1  # lightbox caption, or quote header (replaced by our own)
            return
        if tag == "aside":
            if "quote" in classes:
                self._newline(2)
                who = a.get("data-username")
                post = a.get("data-post")
                header = f"**@{who}**" + (f" (#{post})" if post else "") if who else "Quote"
                same = self.topic_id and a.get("data-topic") == self.topic_id and not self.quote_depth
                self.aside_stack.append(("quote_same" if same else "quote", len(self.out), header))
                self.quote_depth += 1
                self._emit(header + " wrote:")
                self._newline(1)
                self.quote_open = True
            elif "onebox" in classes:
                self.aside_stack.append(("onebox", len(self.out), None))
                self._newline(2)
                self._emit(f"[link preview: {a.get('data-onebox-src') or 'link'}]")
                self._newline(2)
                self.skip = 1
                self.skip_tag = "aside"
            else:
                self.aside_stack.append(("", len(self.out), None))
                self._newline(2)
            return
        if tag == "br":
            self._emit("\n")
        elif tag in ("h1", "h2", "h3", "h4", "h5", "h6"):
            self._newline(2)
            self._emit("#" * int(tag[1]) + " ")
        elif tag == "blockquote":
            if self.quote_open:
                self.quote_open = False
                self.bq_stack.append(False)
            else:
                self._newline(2)
                self.quote_depth += 1
                self.bq_stack.append(True)
        elif tag in ("ul", "ol"):
            self._newline(1)
            self.list_stack.append([tag, 0])
        elif tag == "li":
            self._newline(1)
            indent = "  " * max(0, len(self.list_stack) - 1)
            if self.list_stack and self.list_stack[-1][0] == "ol":
                self.list_stack[-1][1] += 1
                self._emit(f"{indent}{self.list_stack[-1][1]}. ")
            else:
                self._emit(f"{indent}- ")
        elif tag == "pre":
            self._newline(2)
            self._emit("```\n")
            self.pre += 1
        elif tag == "code" and not self.pre:
            self._emit("`")
        elif tag in ("strong", "b"):
            self._emit("**")
        elif tag in ("em", "i"):
            self._emit("*")
        elif tag in ("s", "del", "strike"):
            self._emit("~~")
        elif tag == "a":
            href = a.get("href") or ""
            if href.startswith("/"):
                href = self.base_url + href
            self.link = href
            if "mention" in cls.split():
                self.link = None
            elif self.link:
                self._emit("[")
        elif tag == "img":
            if "avatar" in classes:
                pass
            elif "emoji" in classes:
                self._emit(a.get("alt") or a.get("title") or "")
            else:
                alt = (a.get("alt") or "").strip()
                generic = not alt or re.match(r"(?i)^(image|screenshot|img)[\s_\-\d]*$|.*\.(png|jpe?g|gif|webp)$", alt)
                self._emit("[image]" if generic else f"[image: {alt}]")
        elif tag in ("td", "th"):
            self._emit(" | ")
        elif tag in self.BLOCK:
            self._newline(2 if tag in ("p", "aside") else 1)

    def handle_endtag(self, tag):
        if self.skip:
            if tag in ("div", "span") or tag == "aside" and getattr(self, "skip_tag", None) == "aside":
                self.skip -= 1
                if not self.skip and tag == "aside":
                    self.skip_tag = None
                    self.aside_stack.pop()
            return
        if tag == "aside":
            kind, start, header = self.aside_stack.pop() if self.aside_stack else ("", 0, None)
            if kind.startswith("quote"):
                self.quote_depth = max(0, self.quote_depth - 1)
            if kind == "quote_same":
                # The quoted post is in this thread already: keep a one-line pointer, not a copy.
                body = re.sub(r"(?m)^[> ]+", "", "".join(self.out[start:]))
                body = " ".join(body.split("\n", 1)[1].split()) if "\n" in body else ""
                if len(body) > QUOTE_CHARS:
                    body = body[:QUOTE_CHARS].rsplit(" ", 1)[0] + "…"
                del self.out[start:]
                self._newline(2)
                self._emit(f"> {header}: {body}")
            self._newline(2)
            return
        if tag in ("h1", "h2", "h3", "h4", "h5", "h6", "p"):
            self._newline(2)
        elif tag == "blockquote":
            if not self.bq_stack or self.bq_stack.pop():
                self.quote_depth = max(0, self.quote_depth - 1)
                self._newline(2)
        elif tag in ("ul", "ol"):
            if self.list_stack:
                self.list_stack.pop()
            self._newline(2)
        elif tag == "pre":
            self.pre = max(0, self.pre - 1)
            self._newline(1)
            self._emit("```")
            self._newline(2)
        elif tag == "code" and not self.pre:
            self._emit("`")
        elif tag in ("strong", "b"):
            self._emit("**")
        elif tag in ("em", "i"):
            self._emit("*")
        elif tag in ("s", "del", "strike"):
            self._emit("~~")
        elif tag == "a":
            if self.link:
                self._emit(f"]({self.link})")
            self.link = None
        elif tag in self.BLOCK:
            self._newline(1)

    def handle_data(self, data):
        if self.skip:
            return
        if not self.pre:
            data = re.sub(r"\s+", " ", data)
            if self.at_line_start:
                data = data.lstrip()
        self._emit(data)


def html_to_text(cooked, base_url=BASE_URL, topic_id=None):
    if not cooked:
        return ""
    p = _HTMLToMarkdown(base_url, topic_id)
    p.feed(cooked)
    p.close()
    text = "".join(p.out)
    text = re.sub(r"\[\]\([^)]*\)", "", text)  # empty links, e.g. heading anchors
    text = re.sub(r"[ \t]+\n", "\n", text)
    text = re.sub(r"(?m)^>[> ]*$", "", text)  # lone quote markers
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def strip_tags(s):
    return html.unescape(re.sub(r"<[^>]+>", "", s or "")).strip()


def truncate(text, max_chars, url):
    if max_chars and max_chars > 0 and len(text) > max_chars:
        cut = text[:max_chars].rsplit(" ", 1)[0]
        return cut + f"\n\n[truncated: {len(text) - len(cut)} more chars; full text at {url}]", True
    return text, False


# ----------------------------------------------------------------- domain helpers


def topic_url(slug, topic_id, post_number=None):
    url = f"{BASE_URL}/t/{slug or 'topic'}/{topic_id}"
    return f"{url}/{post_number}" if post_number and post_number > 1 else url


def parse_topic_ref(ref):
    """Accept '1234', '/t/slug/1234', or a full URL. Returns (topic_id, post_number|None)."""
    ref = ref.strip()
    if ref.isdigit():
        return int(ref), None
    path = urllib.parse.urlparse(ref).path if "://" in ref else ref
    m = re.search(r"/t/(?:[^/]+/)?(\d+)(?:/(\d+))?", path)
    if not m:
        raise CLIError(f"cannot parse topic id from {ref!r}", EXIT_USAGE)
    return int(m.group(1)), (int(m.group(2)) if m.group(2) else None)


def tag_names(tags):
    return [t.get("name") or t.get("slug") if isinstance(t, dict) else t for t in (tags or [])]


class Categories:
    def __init__(self, client):
        data = client.get("/categories.json", {"include_subcategories": "true"})
        self.by_id, self.by_slug = {}, {}
        for c in data["category_list"]["categories"]:
            self._add(c, None)
            for s in c.get("subcategory_list") or []:
                self._add(s, c)

    def _add(self, c, parent):
        entry = {
            "id": c["id"], "slug": c["slug"], "name": c["name"],
            "topic_count": c.get("topic_count"), "description": strip_tags(c.get("description_text") or c.get("description")),
            "parent_slug": parent["slug"] if parent else None, "parent_id": parent["id"] if parent else None,
        }
        entry["path"] = f"{entry['parent_slug']}/{entry['slug']}" if parent else entry["slug"]
        self.by_id[c["id"]] = entry
        self.by_slug.setdefault(c["slug"], entry)
        self.by_slug[entry["path"]] = entry

    def resolve(self, ref):
        key = str(ref).strip().lstrip("#").replace(":", "/")
        entry = self.by_id.get(int(key)) if key.isdigit() else self.by_slug.get(key)
        if not entry:
            known = ", ".join(sorted(e["path"] for e in self.by_id.values()))
            raise CLIError(f"unknown category {ref!r}. Known: {known}", EXIT_USAGE)
        return entry

    def label(self, cid):
        e = self.by_id.get(cid)
        return e["path"] if e else (str(cid) if cid else None)


def norm_topic(t, cats):
    accepted = t.get("has_accepted_answer") or bool(t.get("accepted_answer"))
    return {
        "id": t["id"], "title": t.get("title") or strip_tags(t.get("fancy_title")),
        "url": topic_url(t.get("slug"), t["id"]),
        "category": cats.label(t.get("category_id")) if cats else t.get("category_id"),
        "tags": tag_names(t.get("tags")),
        "created_at": t.get("created_at"), "last_posted_at": t.get("last_posted_at") or t.get("bumped_at"),
        "posts_count": t.get("posts_count"), "reply_count": t.get("reply_count"),
        "views": t.get("views"), "like_count": t.get("like_count"), "vote_count": t.get("vote_count"),
        "solved": bool(accepted), "closed": bool(t.get("closed")), "archived": bool(t.get("archived")),
        "pinned": bool(t.get("pinned")),
        "excerpt": strip_tags(t.get("excerpt")) or None,
    }


def day(ts):
    return ts[:10] if ts else "?"


def num(n):
    if n is None:
        return "?"
    return f"{n / 1000:.1f}k".replace(".0k", "k") if n >= 10000 else str(n)


def shown_tags(tags):
    return [t for t in tags or [] if t not in HIDDEN_TAGS]


def snippet(text, n=EXCERPT_CHARS):
    text = " ".join((text or "").split())
    return text if len(text) <= n else text[:n].rsplit(" ", 1)[0] + "…"


def md_topic_line(t):
    bits = [t["category"] or "?"]
    if shown_tags(t["tags"]):
        bits.append(",".join(shown_tags(t["tags"])))
    stats = f"{num(t['posts_count'])} posts · {num(t['views'])} views · {num(t['like_count'])} likes"
    if t.get("vote_count"):
        stats += f" · {num(t['vote_count'])} votes"
    bits.append(stats)
    bits.append(f"{day(t['created_at'])}→{day(t['last_posted_at'])}")
    flags = [f.upper() for f in ("solved", "closed", "archived", "pinned") if t.get(f)]
    line = f"- **{t['title']}** · " + " · ".join(bits + flags) + f"\n  {t['url']}"
    if t.get("excerpt"):
        line += f"\n  > {snippet(t['excerpt'])}"
    return line


def prune(obj):
    """Drop None, empty and False values so --json carries only signal (absent flag = false)."""
    if isinstance(obj, dict):
        out = {k: prune(v) for k, v in obj.items()}
        return {k: v for k, v in out.items() if v is not None and v is not False and v not in ("", [], {})}
    if isinstance(obj, list):
        return [prune(v) for v in obj]
    return obj


def post_role(p):
    """'staff' for Bitwarden employees, 'mod' for volunteer/category moderators, else None."""
    if p.get("staff") or p.get("admin") or p.get("moderator"):
        return "staff"
    if "moderator" in (p.get("user_title") or "").lower() or "moderator" in (p.get("primary_group_name") or "").lower():
        return "mod"
    return None


def is_noise_post(p):
    """System/auto-action posts: 'topic closed', 'moved', solved notices, whispers."""
    return p.get("username") == "system" or p.get("post_type", 1) not in (1,)


def emit(args, data, markdown):
    if args.json:
        print(json.dumps(prune(data), ensure_ascii=False, separators=(",", ":")))
    else:
        print(markdown.rstrip() + "\n")


# ----------------------------------------------------------------------- commands


def cmd_search(client, args):
    # robots.txt disallows /search for all agents; this is a user-driven lookup, not a crawl,
    # so search is exempt by default (still throttled and cached). --strict-robots re-enables it.
    if not args.strict_robots:
        client.robots_exempt = ("/search.json",)
    cats = Categories(client)
    terms = [args.query]
    if args.category:
        c = cats.resolve(args.category)
        terms.append("#" + (f"{c['parent_slug']}:{c['slug']}" if c["parent_slug"] else c["slug"]))
    for tag in args.tag or []:
        terms.append(f"tags:{tag}")
    if args.user:
        terms.append("@" + args.user.lstrip("@"))
    if args.solved:
        terms.append("status:solved")
    if args.after:
        terms.append(f"after:{args.after}")
    if args.before:
        terms.append(f"before:{args.before}")
    if args.in_title:
        terms.append("in:title")
    if args.order:
        terms.append(f"order:{args.order}")
    q = " ".join(terms)

    hits, topics, more = [], {}, False
    for page in range(1, args.pages + 1):
        params = {"q": q}
        if page > 1:
            params["page"] = page
        data = client.get("/search.json", params)
        for t in data.get("topics") or []:
            topics[t["id"]] = t
        posts = data.get("posts") or []
        hits.extend(posts)
        more = bool((data.get("grouped_search_result") or {}).get("more_full_page_results"))
        if not more or not posts or len(hits) >= args.limit:
            break

    results, seen = [], set()
    for p in hits:
        if args.limit and len(results) >= args.limit:
            break
        tid = p.get("topic_id")
        if not args.include_system and p.get("username") == "system":
            continue
        if args.one_per_topic and tid in seen:
            continue
        seen.add(tid)
        t = topics.get(tid, {"id": tid})
        nt = norm_topic(t, cats)
        results.append({
            "topic_id": tid, "post_number": p.get("post_number"), "title": nt["title"],
            "url": topic_url(t.get("slug"), tid, p.get("post_number")),
            "username": p.get("username"), "created_at": p.get("created_at"),
            "like_count": p.get("like_count"), "blurb": snippet(strip_tags(p.get("blurb")).strip(". ")),
            "category": nt["category"], "tags": nt["tags"], "topic_solved": nt["solved"],
            "topic_posts_count": nt["posts_count"], "topic_last_posted_at": nt["last_posted_at"],
        })

    out = {"query": q, "count": len(results), "more_results": more, "results": results}
    lines = [f"# Search: `{q}`", f"{len(results)} hits" + (" (more: raise --pages/--limit)" if more else ""), ""]
    for r in results:
        meta = [r["category"] or "?"]
        if shown_tags(r["tags"]):
            meta.append(",".join(shown_tags(r["tags"])))
        meta.append(f"#{r['post_number']} @{r['username']} {day(r['created_at'])}"
                    + (f" · {r['like_count']} likes" if r["like_count"] else ""))
        if r.get("topic_posts_count"):
            meta.append(f"topic: {num(r['topic_posts_count'])} posts, last {day(r.get('topic_last_posted_at'))}")
        if r["topic_solved"]:
            meta.append("SOLVED")
        lines.append(f"- **{r['title']}** · " + " · ".join(meta) + f"\n  {r['url']}"
                     + (f"\n  > {snippet(r['blurb'])}" if r["blurb"] else ""))
    emit(args, out, "\n".join(lines))


def _fetch_thread(client, topic_id, max_posts, raw, mode):
    """Return (topic, posts, total, raw_map, used_best). mode: auto | best | chrono."""
    data = client.get(f"/t/{topic_id}.json")
    stream = data["post_stream"].get("stream") or []
    posts = {p["id"]: p for p in data["post_stream"]["posts"]}
    used_best = mode == "best" or (mode == "auto" and max_posts and len(stream) > max_posts)
    wanted = stream
    if used_best:
        # Discourse's "best of" filter: up to ~100 top-scored posts, in thread order.
        best = client.get(f"/t/{topic_id}.json", {"filter": "summary"})
        for p in best["post_stream"]["posts"]:
            posts[p["id"]] = p
        wanted = best["post_stream"].get("stream") or stream
    if max_posts:
        wanted = wanted[:max_posts]
    accepted = data.get("accepted_answer") or next(iter(data.get("accepted_answers") or []), {})
    if accepted.get("id") and accepted["id"] in stream and accepted["id"] not in wanted:
        wanted = sorted(wanted + [accepted["id"]], key=stream.index)
    if stream and stream[0] not in wanted:
        wanted = [stream[0]] + wanted
    missing = [pid for pid in wanted if pid not in posts]
    for i in range(0, len(missing), CHUNK):
        chunk = missing[i:i + CHUNK]
        more = client.get(f"/t/{topic_id}/posts.json", [("post_ids[]", pid) for pid in chunk])
        for p in more["post_stream"]["posts"]:
            posts[p["id"]] = p
    ordered = sorted((posts[pid] for pid in wanted if pid in posts), key=lambda p: p["post_number"])
    raw_by_number = {}
    if raw and ordered:
        pages = sorted({(p["post_number"] - 1) // RAW_PAGE + 1 for p in ordered})
        for page in pages:
            text = client.get(f"/raw/{topic_id}", {"page": page}, want_json=False)
            raw_by_number.update(parse_raw_topic(text))
    return data, ordered, len(stream), raw_by_number, used_best


def parse_raw_topic(text):
    """Split /raw/{topic_id} output into {post_number: markdown}."""
    out = {}
    for block in re.split(r"\n-{20,}\n", "\n" + text):
        m = re.match(r"\s*[^\n|]+ \| [^\n|]+ \| #(\d+)\n\n?(.*)", block, re.S)
        if m:
            out[int(m.group(1))] = m.group(2).strip()
    return out


def cmd_thread(client, args):
    topic_id, start_at = parse_topic_ref(args.topic)
    cats = Categories(client)
    mode = "chrono" if args.chrono or start_at else ("best" if args.best else "auto")
    # --brief scans a wider window (whole thread up to 100 posts, else the best-of set) and keeps only key posts.
    fetch_n = max(args.max_posts, BRIEF_SCAN) if args.brief and args.max_posts else args.max_posts
    data, posts, total, raw_map, used_best = _fetch_thread(client, topic_id, fetch_n, args.raw, mode)
    t = norm_topic(data, cats)
    accepted = data.get("accepted_answer") or next(iter(data.get("accepted_answers") or []), {})
    accepted_no = accepted.get("post_number")
    if start_at:
        posts = [p for p in posts if p["post_number"] >= start_at]
    hidden = 0
    if not args.include_system:
        kept = [p for p in posts if not is_noise_post(p)]
        hidden, posts = len(posts) - len(kept), kept
    scanned = len(posts)
    mods_dropped = 0
    if args.brief:
        def likes_of(p):
            return next((a.get("count") or 0 for a in p.get("actions_summary") or [] if a.get("id") == 2), 0)
        key = [p for p in posts if p["post_number"] == 1 or p.get("accepted_answer")
               or p["post_number"] == accepted_no or post_role(p) == "staff"]
        mods = [p for p in posts if post_role(p) == "mod" and p not in key]
        top_mods = sorted(mods, key=likes_of, reverse=True)[:BRIEF_MODS]
        mods_dropped = len(mods) - len(top_mods)
        posts = sorted(key + top_mods, key=lambda p: p["post_number"])

    norm_posts = []
    for p in posts:
        url = topic_url(data.get("slug"), topic_id, p["post_number"])
        body = raw_map.get(p["post_number"]) if args.raw else None
        if body is None:
            body = html_to_text(p.get("cooked"), topic_id=None if args.full_quotes else topic_id)
        body, truncated = truncate(body, args.max_chars, url)
        likes = next((a.get("count") for a in p.get("actions_summary") or [] if a.get("id") == 2), 0)
        norm_posts.append({
            "post_number": p["post_number"], "url": url,
            "username": p.get("username"), "user_title": p.get("user_title"),
            "role": post_role(p),
            "created_at": p.get("created_at"), "reply_to_post_number": p.get("reply_to_post_number"),
            "like_count": likes, "accepted_answer": bool(p.get("accepted_answer")) or p["post_number"] == accepted_no,
            "text": body, "truncated": truncated,
        })

    shown = f"{len(norm_posts)} of {total} posts"
    if args.brief:
        shown += (f" (--brief: first post, accepted answer, all staff posts, top {BRIEF_MODS} moderator posts"
                  + (f" [{mods_dropped} more moderator posts skipped]" if mods_dropped else "")
                  + f"; scanned {scanned}" + (" best-of posts, others may exist" if used_best else " posts") + ")")
    elif used_best:
        shown += " (Discourse 'best of' selection; --chrono for posts in order)"
    elif total > len(posts) + hidden and not start_at:
        shown += " (raise --max-posts, 0 = all, or --best)"
    if hidden:
        shown += f"; {hidden} system posts hidden"
    out = dict(t, total_posts=total, selection="best" if used_best else "chrono",
               accepted_answer_post=accepted_no, accepted_answer_by=accepted.get("username"), posts=norm_posts)
    meta = [t["category"]] + ([",".join(shown_tags(t["tags"]))] if shown_tags(t["tags"]) else []) + [
        f"{num(t['views'])} views · {num(t['like_count'])} likes" + (f" · {num(t['vote_count'])} votes" if t.get("vote_count") else ""),
        f"{day(t['created_at'])}→{day(t['last_posted_at'])}"]
    meta += [f.upper() for f in ("closed", "archived") if t[f]]
    lines = [f"# {t['title']}", f"{t['url']}  (post N: append /N)", " · ".join(meta)]
    if accepted_no:
        lines.append(f"SOLVED: accepted answer #{accepted_no} by @{accepted.get('username')}")
    elif t["solved"]:
        lines.append("SOLVED")
    lines += [shown, ""]
    for p in norm_posts:
        head = f"## #{p['post_number']} @{p['username']}"
        tags = ([p["role"].upper()] if p["role"] else []) + (["ACCEPTED ANSWER"] if p["accepted_answer"] else [])
        if tags:
            head += " [" + ", ".join(tags) + "]"
        head += f" · {day(p['created_at'])}"
        if p["like_count"]:
            head += f" · {p['like_count']} likes"
        if p["reply_to_post_number"]:
            head += f" · re #{p['reply_to_post_number']}"
        lines += [head, p["text"], ""]
    emit(args, out, "\n".join(lines))


def cmd_post(client, args):
    topic_id, url_n = parse_topic_ref(args.topic)
    n = args.post_number or url_n or 1
    raw = client.get(f"/raw/{topic_id}/{n}", want_json=False)
    topic = client.get(f"/t/{topic_id}.json")
    url = topic_url(topic.get("slug"), topic_id, n)
    meta = next((p for p in topic["post_stream"]["posts"] if p["post_number"] == n), None)
    text, truncated = truncate(raw.strip(), args.max_chars, url)
    out = {"topic_id": topic_id, "post_number": n, "title": topic.get("title"), "url": url,
           "username": meta.get("username") if meta else None,
           "created_at": meta.get("created_at") if meta else None,
           "staff": bool(meta.get("staff")) if meta else None, "text": text, "truncated": truncated}
    head = f"# {topic.get('title')} — post #{n}\n{url}"
    if meta:
        head += f"\n@{meta.get('username')}" + (" [STAFF]" if meta.get("staff") else "") + f" · {day(meta.get('created_at'))}"
    emit(args, out, f"{head}\n\n{text}")


def _topic_list(client, args, path, params, title):
    cats = Categories(client)
    data = client.get(path, params)
    tl = data.get("topic_list") or {}
    topics = [norm_topic(t, cats) for t in tl.get("topics") or []]
    if args.limit:
        topics = topics[:args.limit]
    out = {"title": title, "page": params.get("page", 0), "more": bool(tl.get("more_topics_url")), "topics": topics}
    lines = [f"# {title}", f"{len(topics)} topics" + (" · more on next --page" if out["more"] else ""), ""]
    lines += [md_topic_line(t) for t in topics]
    emit(args, out, "\n".join(lines))


def _list_path(client, args, kind):
    """Build the topic-list path for latest/top, scoped to a category or tag."""
    if args.category and args.tag:
        raise CLIError("use --category or --tag, not both", EXIT_USAGE)
    if args.category:
        c = Categories(client).resolve(args.category)
        return f"/c/{c['path']}/{c['id']}/l/{kind}.json", c["path"]
    if args.tag:
        if kind == "latest":
            return f"/tag/{urllib.parse.quote(args.tag)}.json", f"tag {args.tag}"
        return "/top.json", f"tag {args.tag}"
    return f"/{kind}.json", "all categories"


def cmd_latest(client, args):
    path, scope = _list_path(client, args, "latest")
    params = {}
    if args.page:
        params["page"] = args.page
    if args.order:
        params["order"] = args.order
    if args.ascending:
        params["ascending"] = "true"
    _topic_list(client, args, path, params, f"Latest topics: {scope}" + (f" (order: {args.order})" if args.order else ""))


def cmd_top(client, args):
    path, scope = _list_path(client, args, "top")
    params = {"period": args.period}
    if args.tag:
        params["tags"] = args.tag
    if args.page:
        params["page"] = args.page
    _topic_list(client, args, path, params, f"Top topics ({args.period}): {scope}")


def cmd_categories(client, args):
    cats = Categories(client)
    entries = sorted(cats.by_id.values(), key=lambda e: (e["parent_slug"] or e["slug"], e["parent_slug"] is not None, e["slug"]))
    lines = ["# Categories", "Use the path (e.g. `feature-requests/pm-feature-requests`) or a unique slug with --category.", ""]
    for e in entries:
        indent = "  " if e["parent_slug"] else ""
        desc = f" — {e['description'][:140]}" if e["description"] else ""
        lines.append(f"{indent}- `{e['path']}` (id {e['id']}, {e['topic_count']} topics): {e['name']}{desc}")
    emit(args, entries, "\n".join(lines))


def cmd_tags(client, args):
    data = client.get("/tags.json")
    tags = [{"name": t.get("name") or t.get("text"), "count": t.get("count")} for t in data.get("tags") or []]
    for g in (data.get("extras") or {}).get("tag_groups") or []:
        for t in g.get("tags") or []:
            tags.append({"name": t.get("name") or t.get("text"), "count": t.get("count"), "group": g.get("name")})
    seen, uniq = set(), []
    for t in sorted(tags, key=lambda t: -(t["count"] or 0)):
        if t["name"] not in seen:
            seen.add(t["name"])
            uniq.append(t)
    lines = ["# Tags", ""] + [f"- `{t['name']}` ({t['count']})" + (f" [{t['group']}]" if t.get("group") else "") for t in uniq]
    emit(args, uniq, "\n".join(lines))


def cmd_user(client, args):
    name = args.username.lstrip("@")
    u = client.get(f"/u/{urllib.parse.quote(name)}.json")["user"]
    s = client.get(f"/u/{urllib.parse.quote(name)}/summary.json").get("user_summary") or {}
    profile = {
        "username": u.get("username"), "name": u.get("name"), "title": u.get("title"),
        "url": f"{BASE_URL}/u/{u.get('username')}",
        "staff": bool(u.get("admin") or u.get("moderator")), "trust_level": u.get("trust_level"),
        "created_at": u.get("created_at"), "last_posted_at": u.get("last_posted_at"),
        "bio": " ".join(strip_tags(u.get("bio_cooked")).split()) or None,
        "topic_count": s.get("topic_count"), "post_count": s.get("post_count"),
        "likes_received": s.get("likes_received"), "solutions": s.get("solved_count"),
        "days_visited": s.get("days_visited"),
    }
    lines = [f"# @{profile['username']}" + (f" ({profile['name']})" if profile["name"] else ""), profile["url"],
             " · ".join(x for x in [
                 profile["title"], "STAFF" if profile["staff"] else None, f"trust level {profile['trust_level']}",
                 f"joined {day(profile['created_at'])}", f"last post {day(profile['last_posted_at'])}"] if x),
             f"{profile['topic_count']} topics · {profile['post_count']} posts · {profile['likes_received']} likes received"
             + (f" · {profile['solutions']} solutions" if profile["solutions"] is not None else "")]
    if profile["bio"]:
        lines.append(f"> {snippet(profile['bio'])}")
    activity = []
    if args.activity:
        flt = {"topics": 4, "replies": 5}[args.activity]
        offset = 0
        while len(activity) < args.limit:
            items = client.get("/user_actions.json", {"username": name, "filter": flt, "offset": offset}).get("user_actions") or []
            if not items:
                break
            for a in items:
                if not args.include_system and (a.get("action_code") or a.get("post_type", 1) != 1):
                    continue  # auto-close notices etc. attributed to the user
                activity.append({
                    "title": a.get("title"), "url": topic_url(a.get("slug"), a.get("topic_id"), a.get("post_number")),
                    "topic_id": a.get("topic_id"), "post_number": a.get("post_number"),
                    "created_at": a.get("created_at"), "excerpt": strip_tags(a.get("excerpt")),
                })
            offset += len(items)
        activity = activity[:args.limit]
        lines += ["", f"## Recent {args.activity} ({len(activity)})", ""]
        for a in activity:
            lines.append(f"- **{a['title']}** · {day(a['created_at'])}\n  {a['url']}"
                         + (f"\n  > {snippet(a['excerpt'])}" if a["excerpt"] else ""))
    emit(args, dict(profile, activity=activity) if args.activity else profile, "\n".join(lines))


# --------------------------------------------------------------------------- main


class _Parser(argparse.ArgumentParser):
    def error(self, message):
        self.print_usage(sys.stderr)
        print(f"{self.prog}: error: {message}", file=sys.stderr)
        sys.exit(EXIT_USAGE)


def build_parser():
    common = argparse.ArgumentParser(add_help=False)
    g = common.add_argument_group("global options")
    g.add_argument("--json", action="store_true", help="print normalized JSON instead of Markdown")
    g.add_argument("--no-cache", action="store_true", help="bypass the 1h on-disk cache")
    g.add_argument("--max-chars", type=int, default=2500, metavar="N", help="truncate each post at N chars (0 = no limit; default 2500)")
    g.add_argument("--include-system", action="store_true", help="keep @system and auto-action posts (hidden by default)")
    g.add_argument("--ignore-robots", action="store_true", help="do not enforce robots.txt for any path")
    g.add_argument("-v", "--verbose", action="store_true", help="log requests to stderr")

    p = _Parser(prog="bwcommunity", parents=[common],
                description=f"Read-only CLI for the Bitwarden Community forum ({BASE_URL}).",
                epilog="Exit codes: 0 ok, 1 usage, 2 not found, 3 rate-limited/blocked/robots, 4 network.")
    p.add_argument("--version", action="version", version=f"bwcommunity {VERSION}")
    sub = p.add_subparsers(dest="command", required=True, parser_class=_Parser)

    s = sub.add_parser("search", parents=[common], help="full-text search")
    s.add_argument("query")
    s.add_argument("--category", metavar="SLUG", help="category slug or parent/child path")
    s.add_argument("--tag", action="append", metavar="TAG", help="filter by tag (repeatable)")
    s.add_argument("--user", metavar="USERNAME", help="only posts by this user")
    s.add_argument("--solved", action="store_true", help="only topics with an accepted answer")
    s.add_argument("--after", metavar="YYYY-MM-DD")
    s.add_argument("--before", metavar="YYYY-MM-DD")
    s.add_argument("--in-title", action="store_true", help="match titles only")
    s.add_argument("--order", choices=["latest", "views", "likes", "latest_topic"])
    s.add_argument("--pages", type=int, default=1, metavar="N", help="result pages to fetch (50 posts each; default 1)")
    s.add_argument("--limit", type=int, default=15, metavar="N", help="max hits to print (default 15)")
    s.add_argument("--strict-robots", action="store_true", help="refuse to search, since robots.txt disallows /search")
    s.add_argument("--one-per-topic", action="store_true", help="keep only the first hit per topic")
    s.set_defaults(func=cmd_search)

    t = sub.add_parser("thread", parents=[common], help="read a full thread")
    t.add_argument("topic", metavar="TOPIC_ID|URL")
    t.add_argument("--raw", action="store_true", help="use raw Markdown source instead of rendered HTML")
    t.add_argument("--max-posts", type=int, default=40, metavar="N",
                   help="max posts (0 = all; default 40). Longer threads use Discourse's 'best of' selection")
    sel = t.add_mutually_exclusive_group()
    sel.add_argument("--best", action="store_true", help="always use the 'best of' selection")
    sel.add_argument("--chrono", action="store_true", help="first N posts in order, even for long threads")
    t.add_argument("--brief", action="store_true", help="only the first post, accepted answer, staff posts and the top 3 moderator posts")
    t.add_argument("--full-quotes", action="store_true", help="keep full text of quotes from the same thread")
    t.set_defaults(func=cmd_thread)

    po = sub.add_parser("post", parents=[common], help="one post as raw Markdown (from /raw/)")
    po.add_argument("topic", metavar="TOPIC_ID|URL")
    po.add_argument("post_number", type=int, nargs="?", help="defaults to the number in the URL, else 1")
    po.set_defaults(func=cmd_post)

    for name, fn, helptext in (("latest", cmd_latest, "latest topics"), ("top", cmd_top, "top topics for a period")):
        lp = sub.add_parser(name, parents=[common], help=helptext)
        lp.add_argument("--category", metavar="SLUG")
        lp.add_argument("--tag", metavar="TAG")
        lp.add_argument("--page", type=int, default=0, metavar="N", help="0-based page")
        lp.add_argument("--limit", type=int, default=0, metavar="N", help="max topics to print")
        if name == "latest":
            lp.add_argument("--order", choices=["activity", "created", "views", "posts", "likes", "op_likes", "votes"])
            lp.add_argument("--ascending", action="store_true")
        else:
            lp.add_argument("--period", default="monthly", choices=["daily", "weekly", "monthly", "quarterly", "yearly", "all"])
        lp.set_defaults(func=fn)

    sub.add_parser("categories", parents=[common], help="list categories and subcategories").set_defaults(func=cmd_categories)
    sub.add_parser("tags", parents=[common], help="list tags").set_defaults(func=cmd_tags)

    u = sub.add_parser("user", parents=[common], help="user profile and activity")
    u.add_argument("username")
    u.add_argument("--activity", choices=["topics", "replies"])
    u.add_argument("--limit", type=int, default=30, metavar="N", help="max activity items (default 30)")
    u.set_defaults(func=cmd_user)
    return p


def validate_base_url(url):
    """BW_COMMUNITY_URL must be a bare https origin, so the env var cannot point requests at arbitrary schemes or paths."""
    u = urllib.parse.urlparse(url)
    if u.scheme != "https" or not u.hostname or u.username or u.password or u.path not in ("", "/") or u.query or u.fragment:
        raise CLIError(f"BW_COMMUNITY_URL must be an https origin such as {DEFAULT_BASE_URL}, got {url!r}", EXIT_USAGE)


def main(argv=None):
    args = build_parser().parse_args(argv)
    try:
        validate_base_url(BASE_URL)
    except CLIError as e:
        print(f"bwcommunity: {e}", file=sys.stderr)
        return e.code
    if args.max_chars < 0:
        print("bwcommunity: error: --max-chars must be >= 0", file=sys.stderr)
        return EXIT_USAGE
    client = Client(use_cache=not args.no_cache, honour_robots=not args.ignore_robots, verbose=args.verbose)
    try:
        args.func(client, args)
    except CLIError as e:
        print(f"bwcommunity: {e}", file=sys.stderr)
        return e.code
    except KeyboardInterrupt:
        return 130
    except BrokenPipeError:
        return EXIT_OK
    return EXIT_OK


if __name__ == "__main__":
    sys.exit(main())
