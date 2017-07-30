import os
import constants as c
from build_structures import PlatformConfig
from vagrant_build import VagrantBuildSystem, VagrantBuildStep
import shared_build_steps as u
import cmake_utils as cmu

macos_config = PlatformConfig(c.target_macos, [c.arch_x86, c.arch_x64])

macos_config.set_cross_configs({
    "vagrant": VagrantBuildStep(
        platform=c.target_macos,
        host_cwd="$CWD/vagrant/$PLATFORM",
        build_cwd="/Users/vagrant/j2v8",
        pre_build_cmd = u.setEnvVar("VAGRANT_FILE_SHARE_TYPE", "smb" if os.name == "nt" else "virtualbox")[0],
    )
})

macos_config.set_cross_compilers({
    "vagrant": VagrantBuildSystem
})

macos_config.set_file_abis({
    c.arch_x64: "x86_64",
    c.arch_x86: "x86_32",
})

#-----------------------------------------------------------------------
def build_node_js(config):
    return [
        "cd ./node",
        """./configure              \
            --without-intl          \
            --without-inspector     \
            --dest-cpu=$ARCH        \
            --without-snapshot      \
            --enable-static""",
        "make -j4",
    ]

macos_config.build_step(c.build_node_js, build_node_js)
#-----------------------------------------------------------------------
def build_j2v8_cmake(config):
    cmake_vars = cmu.setAllVars(config)

    # NOTE: uses Python string interpolation (see: https://stackoverflow.com/a/4450610)
    return \
        u.shell("mkdir", u.cmake_out_dir) + \
        ["cd " + u.cmake_out_dir] + \
        u.shell("rm", "CMakeCache.txt CMakeFiles/") + \
        ["""cmake \
            -DCMAKE_BUILD_TYPE=Release \
            %(cmake_vars)s \
            ../../ \
        """
        % locals()]

macos_config.build_step(c.build_j2v8_cmake, build_j2v8_cmake)
#-----------------------------------------------------------------------
def build_j2v8_jni(config):
    return [
        "cd " + u.cmake_out_dir,
        "make -j4",
    ]

macos_config.build_step(c.build_j2v8_jni, build_j2v8_jni)
#-----------------------------------------------------------------------
def build_j2v8_java(config):
    return \
        u.clearNativeLibs(config) + \
        u.copyNativeLibs(config) + \
        u.setBuildEnv(config) + \
        [u.build_cmd] + \
        u.copyOutput(config)

macos_config.build_step(c.build_j2v8_java, build_j2v8_java)
#-----------------------------------------------------------------------
def build_j2v8_junit(config):
    return \
        u.setBuildEnv(config) + \
        [u.run_tests_cmd]

macos_config.build_step(c.build_j2v8_junit, build_j2v8_junit)
#-----------------------------------------------------------------------
