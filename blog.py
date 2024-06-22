import functools
import pathlib
from dataclasses import dataclass
from typing import Callable

from fasthtml.common import *
import yaml
import uvicorn


markdown_js = """
import { marked } from "https://cdn.jsdelivr.net/npm/marked/lib/marked.esm.js";
import { proc_htmx} from "https://cdn.jsdelivr.net/gh/answerdotai/fasthtml-js/fasthtml.js";
proc_htmx('.markdown', e => e.innerHTML = marked.parse(e.textContent));
"""

# app = FastHTML()
app = FastHTMLWithLiveReload(hdrs=(
    MarkdownJS(),
    HighlightJS(langs=['python', 'javascript', 'html', 'css']),
    Link(rel='stylesheet', href='https://cdn.jsdelivr.net/npm/sakura.css/css/sakura.css', type='text/css')
)
)

@dataclass
class BlogPost():
    title: str
    slug: str
    timestamp: str
    description: str

    def __xt__(self):
        return Span(
                H2(
                    A(self.title, href=f"/posts/{self.slug}")
                ),
                P(self.description),
                Small(
                    Time(self.timestamp))
                )


@functools.lru_cache
def list_posts(published: bool = True, posts_dirname="posts") -> list[dict]:
    posts: list[dict] = []
    for post in pathlib.Path(".").glob(f"{posts_dirname}/*.md"):
        raw: str = post.read_text().split("---")[1]
        data: dict = yaml.safe_load(raw)
        data["slug"] = post.stem
        posts.append(data)

    posts = [x for x in filter(lambda x: x["published"] is True, posts)]

    posts.sort(key=lambda x: x["date"], reverse=True)
    return [x for x in filter(lambda x: x["published"] is published, posts)]

def Time(time: str) -> str:
    return time

@app.get("/")
def articles():
    articles = []
    for post in list_posts():
        articles.append(
            BlogPost(
                title=post["title"],
                slug=post["slug"],
                timestamp=post["date"],
                description=post.get("description", "")
            )
        )
    return Title("Daniel Roy Greenfeld"), Main(
        Section(
            H1(f'All Articles ({len(articles)})'),
            P('Everything written by Daniel Roy Greenfeld for the past 19 years'),
            *articles
        )
    )

@app.get("/posts/{slug}")
def article(slug: str):
    post = [
            x for x in filter(lambda x: x["slug"] == slug, list_posts())
        ][0]
    content = pathlib.Path(f"posts/{slug}.md").read_text().split("---")[2]
    return Title(post["title"]), Main(
        A("Back to all articles", href="/"),
        Section(
            H1(post["title"]),
            Div(
                content,
                cls="marked"
            )
        )
    )
    

if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=int(os.getenv("PORT", default=8000)))