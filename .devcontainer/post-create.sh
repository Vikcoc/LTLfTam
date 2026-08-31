#!/bin/bash
set -e

# 1. Install Spot via Conda
conda install -c conda-forge -y spot

# 2. Install Debian APT dependencies
sudo apt-get update
sudo apt-get install -y \
  maude \
  graphviz \
  docker.io \
  texlive-latex-recommended \
  texlive-latex-extra \
  texlive-fonts-recommended \
  texlive-xetex \
  texlive-bibtex-extra \
  texlive-lang-european \
  texlive-lang-english \
  biber \
  fonts-freefont-ttf \
  fonts-liberation \
  fontconfig \
  latexmk

# 3. Install Python packages
pip install --upgrade pip
pip install declare4py pm4py

# 4. Pull Lydia Docker image & create wrapper script
docker pull --platform linux/amd64 whitemech/lydia:latest

sudo tee /usr/local/bin/lydia > /dev/null << 'EOF'
#!/bin/sh
FILE=""
NEW_ARGS=""
SKIP_NEXT=0
for arg in "$@"; do
  if [ "$SKIP_NEXT" -eq 1 ]; then
    FILE="$arg"
    NEW_ARGS="$NEW_ARGS /tmp/formula_in_container.txt"
    SKIP_NEXT=0
    continue
  fi
  case "$arg" in
    --file=*)
      FILE="${arg#*=}"
      NEW_ARGS="$NEW_ARGS --file=/tmp/formula_in_container.txt"
      ;;
    --file)
      FILE=""
      NEW_ARGS="$NEW_ARGS --file"
      SKIP_NEXT=1
      ;;
    *)
      NEW_ARGS="$NEW_ARGS $arg"
      ;;
  esac
done

if [ -n "$FILE" ] && [ -f "$FILE" ]; then
  cat "$FILE" | docker run --platform linux/amd64 --rm -i whitemech/lydia:latest sh -c "cat > /tmp/formula_in_container.txt && lydia $NEW_ARGS"
else
  docker run --platform linux/amd64 --rm -i whitemech/lydia:latest lydia "$@"
fi
EOF

sudo chmod +x /usr/local/bin/lydia