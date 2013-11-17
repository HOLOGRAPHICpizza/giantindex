cleanstring(){ printf '%s' "$1" | iconv -cs -f UTF-8 -t UTF-8 | tr -d "\n'\"\r|" ; }
relpath(){ python -c "import os.path; print os.path.relpath('`cleanstring "$1"`','`cleanstring "$2"`')" ; }
