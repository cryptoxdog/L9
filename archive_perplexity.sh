#!/bin/bash
# =============================================================================
# Archive Perplexity Files
# =============================================================================
# Run this script to move all scattered Perplexity files to _Archive_Perplexity/
# =============================================================================

set -e
cd "$(dirname "$0")"

echo "🗄️  Archiving Perplexity files..."

# Create archive directories
mkdir -p _Archive_Perplexity/{docs,scripts,services_research,services_research_factory,core_schemas,config,generated,tests}

# 1. Move docs/Perplexity (entire folder)
if [ -d "docs/Perplexity" ]; then
    echo "  → Moving docs/Perplexity..."
    mv docs/Perplexity/* _Archive_Perplexity/docs/
    rmdir docs/Perplexity
fi

# 2. Move scripts (perplexity/research related)
echo "  → Moving scripts..."
for f in \
    scripts/send_perplexity_spec_request.py \
    scripts/run_single_deep_research.py \
    scripts/delegate_deep_research.py \
    scripts/batch_generate_specs.py \
    scripts/extract_perplexity_pack.py \
    scripts/factory_extract.py \
    scripts/test_research_factory.py \
    scripts/modules_example.txt; do
    [ -f "$f" ] && mv "$f" _Archive_Perplexity/scripts/ && echo "    ✓ $f"
done

# 3. Move services/research (EXCEPT tools/)
echo "  → Moving services/research (except tools/)..."
[ -d "services/research/agents" ] && mv services/research/agents _Archive_Perplexity/services_research/
[ -f "services/research/memory_adapter.py" ] && mv services/research/memory_adapter.py _Archive_Perplexity/services_research/

# 4. Move services/research_factory (entire folder)
if [ -d "services/research_factory" ]; then
    echo "  → Moving services/research_factory..."
    mv services/research_factory/* _Archive_Perplexity/services_research_factory/
    rmdir services/research_factory 2>/dev/null || rm -rf services/research_factory
fi

# 5. Move core/schemas research_factory files
echo "  → Moving core/schemas research_factory files..."
for f in \
    core/schemas/research_factory_state.py \
    core/schemas/research_factory_models.py \
    core/schemas/research_factory_nodes.py; do
    [ -f "$f" ] && mv "$f" _Archive_Perplexity/core_schemas/ && echo "    ✓ $f"
done
[ -f "core/schemas/tests/test_research_factory.py" ] && mv core/schemas/tests/test_research_factory.py _Archive_Perplexity/tests/

# 6. Move config files
echo "  → Moving config files..."
[ -f "config/agents/research-agent-v1.yaml" ] && mv config/agents/research-agent-v1.yaml _Archive_Perplexity/config/
[ -f "config/research_settings.py" ] && mv config/research_settings.py _Archive_Perplexity/config/

# 7. Move generated specs
echo "  → Moving generated specs..."
[ -f "generated/specs/config_loader.yaml" ] && mv generated/specs/config_loader.yaml _Archive_Perplexity/generated/

# 8. Move tests
echo "  → Moving tests..."
if [ -d "tests/services/research_factory" ]; then
    mv tests/services/research_factory/* _Archive_Perplexity/tests/ 2>/dev/null
    rmdir tests/services/research_factory 2>/dev/null || true
    rmdir tests/services 2>/dev/null || true
fi

echo ""
echo "✅ Archive complete!"
echo ""
echo "Archived to: _Archive_Perplexity/"
echo ""
echo "NOT touched (as requested):"
echo "  - api/"
echo "  - services/research/tools/"
echo ""
echo "To undo: git checkout -- ."


