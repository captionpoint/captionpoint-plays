#!/bin/bash
# Setup script for CaptionPoint PDF tools

echo "🔧 Setting up CaptionPoint PDF parser..."

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating Python virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔌 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo ""
echo "✅ Setup complete!"
echo ""
echo "To use the PDF parser:"
echo "  1. Activate the environment:"
echo "     source venv/bin/activate"
echo ""
echo "  2. Run the parser:"
echo "     python pdf_to_captionpoint.py script.pdf output.md"
echo ""
echo "  3. When done, deactivate:"
echo "     deactivate"
