Coding Instructions for the bgen repository:

Build:
  ./waf configure
  ./waf

Testing:
  ./build/test/unit/test_bgen
  ./build/apps/bgenix -g example/example.16bits.bgen -list

Please run these steps after code changes to ensure everything compiles and tests pass.
