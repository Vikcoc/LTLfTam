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
  curl \
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

# 3. Download & install Tamarin Prover dynamically from latest GitHub release
TMP_DIR=$(mktemp -d)

TAMARIN_URL=$(python3 -c "
import urllib.request, json
try:
    req = urllib.request.Request('https://api.github.com/repos/tamarin-prover/tamarin-prover/releases/latest', headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req) as resp:
        data = json.loads(resp.read().decode())
        for asset in data.get('assets', []):
            url = asset.get('browser_download_url', '')
            if 'linux' in url.lower() and url.endswith('.tar.gz'):
                print(url)
                break
except Exception:
    pass
")

if [ -z "$TAMARIN_URL" ]; then
  TAMARIN_URL="https://github.com/tamarin-prover/tamarin-prover/releases/download/1.8.0/tamarin-prover-1.8.0-linux64-X86_64.tar.gz"
fi

echo "Downloading Tamarin from: $TAMARIN_URL"
curl -fsSL "$TAMARIN_URL" -o "$TMP_DIR/tamarin.tar.gz"
tar -xzf "$TMP_DIR/tamarin.tar.gz" -C "$TMP_DIR"
sudo mv "$TMP_DIR"/tamarin-prover /usr/local/bin/
sudo chmod +x /usr/local/bin/tamarin-prover
rm -rf "$TMP_DIR"

# 4. Install Python packages
pip install --upgrade pip
pip install declare4py pm4py

# 5. Pull Lydia Docker image & create wrapper script
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