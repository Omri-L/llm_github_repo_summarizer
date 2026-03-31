# FILE selection config
IMPORTANT_FILES = [
    "readme.md", "requirements.txt", "pyproject.toml", "package.json", 
    "setup.py", "dockerfile", "cargo.toml", "go.mod", "tsconfig.json",
    "makefile", "architecture.md"
]

IGNORED_DIRS = ["node_modules", ".git", "dist", "build", "__pycache__"]
IGNORED_FILE_TYPES = (".png", ".jpg", ".zip", ".exe", ".bin", ".so")
SRC_FILE_TYPES = (".py", ".js", ".ts", ".tsx", ".jsx", ".go", ".rs", ".c", ".cpp", ".cc", ".cxx", ".h", ".hpp", 
                  ".java", ".kt", ".cs", ".swift", ".dart", ".php", ".rb", ".scala", ".lua", ".sh", ".ps1")

PRIORITY_FOLDERS = ["/src/", "/lib/", "/app/"]
PRIORITY_FILENAMES = ["main", "app", "index", "server", "core"] 
NON_PRIORITY_FOLDERS = ["/tests/", "/examples/", "/scripts/"]

SRC_FILES_LIMIT = 5

# conext building config
MAX_CHARS = 8000
MANIFEST_FILES = ["readme", "toml", "json", "yaml"]
CHAR_LIMITS_PER_FILE = 500
CHAR_LIMITS_MANIFEST = 2000
TRUCATED_MANIFEST_CHAR_LIMIT = 500


def is_valid_path(path):
    """
    Filters out irrelevant paths by excluding ignored directories and binary file types, 
    ensuring only meaningful source files are processed.
    """
    lower = path.lower()

    if any(d in lower for d in IGNORED_DIRS):
        return False

    if lower.endswith(IGNORED_FILE_TYPES):
        return False

    return True

def get_file_score(path):
    """
    Assigns score to file based on its location and name, 
    prioritizing core logic files and penalizing non-essential ones.
    """
    score = 0
    name = path.split("/")[-1].lower()
    
    # Priority folders
    if any(folder in path.lower() for folder in PRIORITY_FOLDERS):
        score += 10
    
    # Priority filenames
    if any(key in name for key in PRIORITY_FILENAMES):
        score += 20
        
    # Penalty for non-core folders
    if any(folder in path.lower() for folder in NON_PRIORITY_FOLDERS):
        score -= 50
        
    return score

def select_files(tree):
    """
    Selects the most informative files from the repository tree by:
    1. Always including critical files.
    2. Scoring and ranking source files.
    3. Returning a prioritized list for context building.
    """
    important = []
    source_candidates = []
    
    for f in tree:
        path = f["path"]
        if not is_valid_path(path) or f["type"] != "blob":
            continue
            
        name = path.split("/")[-1].lower()
        
        # 1. include critical files regardless of score
        if name in IMPORTANT_FILES:
            important.append(path)
        
        # 2. potential source files to score and rank 
        elif path.endswith(SRC_FILE_TYPES):
            score = get_file_score(path)
            source_candidates.append((path, score))

    # 3. sort candidates by score + limit to to N
    source_candidates.sort(key=lambda x: x[1], reverse=True)
    top_sources = [f[0] for f in source_candidates]
    
    return important + top_sources[:SRC_FILES_LIMIT]


def build_context(owner, repo, files, downloader, tree):
    """
    Constructs the text context sent to the LLM by:
    1. Downloading selected files.
    2. Truncating content based on importance.
    3. Enforcing a global size limit.
    """

    context = []
    total_chars = 0

    print(f"Selected {len(files)} files for context building.")

    # Add selected file contents
    for f in files:
        content = downloader(owner, repo, f)
        if not content:
            continue

        is_manifest = any(m in f.lower() for m in MANIFEST_FILES)
        char_limit = CHAR_LIMITS_MANIFEST if is_manifest else CHAR_LIMITS_PER_FILE

        content = content[:char_limit]

        block = f"\nFILE: {f}\n{content}\n"

        if total_chars + len(block) > MAX_CHARS:
            if is_manifest and total_chars < MAX_CHARS:
                content = content[:TRUCATED_MANIFEST_CHAR_LIMIT]
                block = f"\nFILE: {f} (truncated)\n{content}\n"
            else:
                continue

        context.append(block)
        total_chars += len(block)

        if total_chars >= MAX_CHARS:
            break

    return "\n".join(context)