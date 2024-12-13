import json

from conan import ConanFile
from conan.errors import ConanException
from conan.tools.files import copy, save
from pathlib import Path


class npm:
    def __init__(self, conanfile: ConanFile):
        self._conanfile = conanfile

    def generate(self):
        if self._conanfile.settings.os != "Emscripten":
            self._conanfile.output.error("Can only deploy to NPM when build for Emscripten")
            raise ConanException("Can only deploy to NPM when build for Emscripten")

        root_package = [dep for dep in self._conanfile.dependencies.direct_host.values()][0]

        # Copy the *.js and *.d.ts
        copy(self._conanfile, "*.js", src=root_package.package_folder, dst=self._conanfile.generators_folder)
        copy(self._conanfile, "*.d.ts", src=root_package.package_folder, dst=self._conanfile.generators_folder)

        # Create the package.json
        save(self._conanfile, str(Path(self._conanfile.generators_folder, "package.json")),
             json.dumps(root_package.conf_info.get(f"user.{root_package.ref.name.lower()}:package_json")))

        # Create the .npmrc file
        save(self._conanfile, str(Path(self._conanfile.generators_folder, ".npmrc")),
             "//npm.pkg.github.com/:_authToken=${GITHUB_TOKEN}\n@ultimaker:registry=https://npm.pkg.github.com\nalways-auth=true")
