from conans import ConanFile, CMake
import os
from conans.tools import download, unzip, replace_in_file
from conans import CMake, ConfigureEnvironment
import patch

class GeosConan(ConanFile):
    name = "Geos"
    version = "3.4.3"
    settings = "os", "compiler", "build_type", "arch"
    folder = "geos-%s" % version
    generators = "cmake"
    url = "http://svn.osgeo.org/geos"
    license = "LGPL"
    options = {"shared": [True, False], "static": [True, False]}
    default_options = '''shared=True
    static=False'''
    exports = "geos-%s.patch" % version

    def source(self):
        zip_name = "geos-%s.tar.bz2" % self.version
        download("http://download.osgeo.org/geos/%s" % zip_name, zip_name)
        unzip(zip_name)
        os.unlink(zip_name)
        if self.settings.os != "Windows":
            self.run("chmod +x ./%s/configure" % self.folder)

        for p in self.exports:
            if os.path.exists(p):
                pset = patch.fromfile(p)
                pset.apply()
			
    def build(self):
        cmake = CMake(self.settings)
        if not os.path.exists('build'):
            os.makedirs('build')
        shared = "--target geos " if self.options.shared else ""
        static = "--target geos-static " if self.options.static else ""
        self.run('cmake ../%s %s -DGEOS_ENABLE_TESTS=OFF ' % (self.folder, cmake.command_line), cwd='build')
        self.run('cmake --build build ' + shared + static + cmake.build_config)

    def package(self):
        """ Define your conan structure: headers, libs and data. After building your
            project, this method is called to create a defined structure:
        """
        self.copy(pattern="*.h", dst="include", src="%s/include" % self.folder, keep_path=True)
        self.copy("*.lib", dst="lib", keep_path=False)
        self.copy(pattern="*.dll", dst="lib", keep_path=False)        
        self.copy(pattern="*.a", dst="lib", keep_path=False)
        self.copy(pattern="*.so*", dst="lib", keep_path=False)
        self.copy(pattern="*.dylib*", dst="lib", keep_path=False)

    def package_info(self):
        if self.settings.build_type == "Debug":
            libname = "geos"    # ?
        else:
            libname = "geos"
        self.cpp_info.libs = [libname]
