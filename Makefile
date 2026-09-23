PYTHON ?= python3
CXX ?= g++
# Keep assertions enabled in inherited verification scripts.
export PYTHONOPTIMIZE :=
.PHONY: check paper verify test-references manifest package release-check
check: src/bruteforce_contain
	$(PYTHON) src/check_certificate.py
	$(PYTHON) src/check_provenance.py
	$(PYTHON) src/check_recount_records.py
	$(PYTHON) src/compare_archive_S8.py
	$(PYTHON) src/test_cluster_cli.py
	$(PYTHON) src/test_chi_components_cli.py
	$(PYTHON) src/test_verification.py
	$(PYTHON) src/check_revision7_math.py
	$(PYTHON) src/test_release_tools.py
paper:
	bash src/build_manuscript.sh
test-references:
	$(PYTHON) src/test_reference_check.py
verify:
	bash -o pipefail -c 'bash src/verify.sh 2>&1 | tee verification.log'
	$(PYTHON) src/check_revision7_math.py
manifest:
	$(PYTHON) src/package_repository.py --manifest-only
package:
	$(PYTHON) src/package_repository.py
release-check:
	$(PYTHON) src/configure_release.py --check

# A clean checkout must not depend on an untracked executable.
src/bruteforce_contain: src/bruteforce_contain.cpp
	$(CXX) -O3 -std=c++17 $< -o $@
