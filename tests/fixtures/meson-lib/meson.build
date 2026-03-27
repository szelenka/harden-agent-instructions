project('meson-lib', 'c',
  version : '0.1.0',
  default_options : ['warning_level=3', 'c_std=c17'])

inc = include_directories('include')

lib = library('mathutil', 'src/mathutil.c',
  include_directories : inc,
  install : true)

pkg = import('pkgconfig')
pkg.generate(lib)

install_headers('include/mathutil.h')

test_exe = executable('test_mathutil', 'tests/test_mathutil.c',
  include_directories : inc,
  link_with : lib)

test('unit_tests', test_exe)
