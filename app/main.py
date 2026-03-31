from fastapi import FastAPI
from fastapi.responses import JSONResponse

from .schemes import SummarizeRequest
from .github_func import parse_repo, get_repo_tree, download_file
from .repo_processor import select_files, build_context
from .llm import call_llm

app = FastAPI()


@app.post("/summarize")
def summarize(req: SummarizeRequest):
    try:
        owner, repo = parse_repo(req.github_url)

        tree = get_repo_tree(owner, repo)
        files = select_files(tree)
        
        if not files:
            return JSONResponse(
                status_code=400,
                content={
                    "status": "error",
                    "message": "Repository contains no usable files or no files"
                }
            )

        context = build_context(owner, repo, files, download_file, tree)

        result = call_llm(context)

        return result

    except ValueError as e:
        return JSONResponse(
            status_code=400,
            content={"status": "error", "message": str(e)}
        )

    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"status": "error", "message": str(e)}
        )
