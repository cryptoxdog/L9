#!/bin/bash
# =============================================================================
# Archive Perplexity Files - DRY RUN
# =============================================================================
# Shows what WOULD be moved without actually moving anything
# =============================================================================

cd "$(dirname "$0")"

echo "🔍 DRY RUN - Archive Perplexity Files"
echo "======================================"
echo ""

# 1. docs/Perplexity
echo "📁 docs/Perplexity/ → _Archive_Perplexity/docs/"
if [ -d "docs/Perplexity" ]; then
    find docs/Perplexity -type f | while read f; do echo "   $f"; done
    echo "   ($(find docs/Perplexity -type f | wc -l | tr -d ' ') files)"
else
    echo "   ⚠️  NOT FOUND"
fi
echo ""

# 2. Scripts
echo "📁 scripts/ → _Archive_Perplexity/scripts/"
for f in \
    scripts/send_perplexity_spec_request.py \
    scripts/run_single_deep_research.py \
    scripts/delegate_deep_research.py \
    scripts/batch_generate_specs.py \
    scripts/extract_perplexity_pack.py \
    scripts/factory_extract.py \
    scripts/test_research_factory.py \
    scripts/modules_example.txt; do
    if [ -f "$f" ]; then
        echo "   ✓ $f"
    else
        echo "   ✗ $f (not found)"
    fi
done
echo ""

# 3. services/research (except tools/)
echo "📁 services/research/ (except tools/) → _Archive_Perplexity/services_research/"
if [ -d "services/research/agents" ]; then
    find services/research/agents -type f | while read f; do echo "   $f"; done
fi
[ -f "services/research/memory_adapter.py" ] && echo "   services/research/memory_adapter.py"
echo ""

# 4. services/research_factory
echo "📁 services/research_factory/ → _Archive_Perplexity/services_research_factory/"
if [ -d "services/research_factory" ]; then
    find services/research_factory -type f | while read f; do echo "   $f"; done
    echo "   ($(find services/research_factory -type f | wc -l | tr -d ' ') files)"
else
    echo "   ⚠️  NOT FOUND"
fi
echo ""

# 5. core/schemas research_factory files
echo "📁 core/schemas/ research_factory files → _Archive_Perplexity/core_schemas/"
for f in \
    core/schemas/research_factory_state.py \
    core/schemas/research_factory_models.py \
    core/schemas/research_factory_nodes.py \
    core/schemas/tests/test_research_factory.py; do
    if [ -f "$f" ]; then
        echo "   ✓ $f"
    else
        echo "   ✗ $f (not found)"
    fi
done
echo ""

# 6. config files
echo "📁 config/ → _Archive_Perplexity/config/"
for f in \
    config/agents/research-agent-v1.yaml \
    config/research_settings.py; do
    if [ -f "$f" ]; then
        echo "   ✓ $f"
    else
        echo "   ✗ $f (not found)"
    fi
done
echo ""

# 7. generated specs
echo "📁 generated/ → _Archive_Perplexity/generated/"
[ -f "generated/specs/config_loader.yaml" ] && echo "   ✓ generated/specs/config_loader.yaml" || echo "   ✗ generated/specs/config_loader.yaml (not found)"
echo ""

# 8. tests
echo "📁 tests/ → _Archive_Perplexity/tests/"
if [ -d "tests/services/research_factory" ]; then
    find tests/services/research_factory -type f | while read f; do echo "   $f"; done
else
    echo "   ✗ tests/services/research_factory/ (not found)"
fi
echo ""

# Summary
echo "======================================"
echo "❌ NOT TOUCHED (as requested):"
echo "   - api/"
echo "   - services/research/tools/"
echo ""
echo "To execute: ./archive_perplexity.sh"


