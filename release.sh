#!/bin/bash
#
# release.sh
#
# Copyright (C) 2018, Branko Majic <branko@majic.rs>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

program="release.sh"

function short_usage() {
    cat <<EOF
$program, interactive utility release script

Usage: $program [OPTIONS] {prepare,publish} version

Run $program -h for more details.
EOF
}

function usage() {
    cat <<EOF
$program, interactive utility release script

Usage: $program [OPTIONS] {prepare,publish} version

$program is a utility release script. The intention is to make the
release process easier in a project.

Two positional arguments are required - operation, and version.

No matter what operation is selected, a number of validation steps are
performed to ensure the release is prepared/published from a correct
working environment. For example, if there are uncommitted changes,
release process wil fail.

When specifying the version, the following limitations should be kept
in mind:

- Version must be specified in format MAJOR.MINOR.PATCH, where MAJOR,
  MINOR, and PATCH are non-negative integers. It is not allowed to
  have both MAJOR and MINOR set to zero (0).
- Version 0.0.0 is treated as development version, and cannot be used
  for releases.
- Releases from master branch are supported only for new major/minor
  releases (where patch number is 0). E.g. 0.1.0, 1.0.0.
- Releases from maintenance branches are supported only for new patch
  releases that the intended maintenance branch covers.

The following operations are supported:

prepare

    Prepares the release by making the necessary changes in the local
    git repository.The process involves:

    - Ensuring that all tests are passing.
    - Updating version information in release notes and package setup
      script. This change is then committed using a signed commit.
    - Starting a new section in the release notes (in the master
      and/or maintenance branch), and updating the version in package
      setup script to mark it as development. This change is then
      committed using a signed commit.
    - Creating the maintenance branch if necessary. This action is
      only performed when releasing from the master branch. Naming
      convention for maintenance branch is "maintenance/MAJOR.MINOR".

publish

    Publishes the specified release. The process involves:

    - Building the source and binary distribution using the specified
      tag.
    - Pushing changes from local master and/or maintenance branch to
      the upstream (origin) repository.
    - Pushing tag corresponding to the specified version number to the
      upstream (origin) repository.
    - Uploading the source and binary distribution to PyPI.

$program accepts the following options:

    -r pypi_repository_url
        Use the designated PyPI repository URL. Default is
        https://pypi.org/legacy/.
    -d
        Enable debug mode. Produces more output helpful for debugging
        the script itself.
    -v
        Show script licensing information.
    -h
        Show usage help.


Please report bugs and send feature requests to <branko@majic.rs>.
EOF
}

function version_and_licensing() {
    cat <<EOF
$program

+-----------------------------------------------------------------------+
| Copyright (C) 2018, Branko Majic <branko@majic.rs>                    |
|                                                                       |
| This program is free software: you can redistribute it and/or modify  |
| it under the terms of the GNU General Public License as published by  |
| the Free Software Foundation, either version 3 of the License, or     |
| (at your option) any later version.                                   |
|                                                                       |
| This program is distributed in the hope that it will be useful,       |
| but WITHOUT ANY WARRANTY; without even the implied warranty of        |
| MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the         |
| GNU General Public License for more details.                          |
|                                                                       |
| You should have received a copy of the GNU General Public License     |
| along with this program.  If not, see <http://www.gnu.org/licenses/>. |
+-----------------------------------------------------------------------+

EOF
}

# Set-up colours for message printing if we're not piping and terminal is
# capable of outputting the colors.
_color_terminal=$(tput colors 2>&1)
if [[ -t 1 ]] && (( ${_color_terminal} > 0 )); then
    _text_bold=$(tput bold)
    _text_white=$(tput setaf 7)
    _text_blue=$(tput setaf 6)
    _text_green=$(tput setaf 2)
    _text_yellow=$(tput setaf 3)
    _text_red=$(tput setaf 1)
    _text_reset=$(tput sgr0)
else
    _text_bold=""
    _text_white=""
    _text_blue=""
    _text_green=""
    _text_yellow=""
    _text_red=""
    _text_reset=""
fi

# Set-up functions for printing coloured messages.
function debug() {
    if [[ $debug != 0 ]]; then
        echo -e "${_text_bold}${_text_blue}[DEBUG]${_text_reset}" "$@"
    fi
}

function info() {
    echo -e "${_text_bold}${_text_white}[INFO] ${_text_reset}" "$@"
}

function success() {
    echo -e "${_text_bold}${_text_green}[OK]   ${_text_reset}" "$@"
}

function warning() {
    echo -e "${_text_bold}${_text_yellow}[WARN] ${_text_reset}" "$@"
}

function error() {
    echo "${_text_bold}${_text_red}[ERROR]${_text_reset}" "$@" >&2
}

#
# Cleanup function that gets called once the script exits. The purpose
# of this function is to provide a single cleanup point that gets
# executed no matter what when the script exits.
#
# The function will:
#
# - Perform a hard reset of the current branch to its pre-release
#   state if "cleanup_reset" variable is set to "1". Function depends
#   on "initial_changeset" variable being set to the correct changeset
#   value.
#
# - Remove the maintenance branch if "cleanup_maintenance_branch"
#   variable is set to "1". Branch name is read from variable
#   "maintenance_branch".
#
# - Remove the tag if "cleanup_tag" variable is set to "1". Tag value
#   will be read from variable "version".
#
function cleanup() {
    # Store the current exit code so we can preserve it.
    exit_code="$?"

    if [[ $cleanup_reset == 1 || $cleanup_maintenance_branch == 1 || $cleanup_tag == 1 ]]; then
        warning "Release process has failed. Starting the cleanup process."
    fi

    if [[ $cleanup_reset == 1 ]]; then
        info "Performing hard reset to changeset: $initial_changeset"
        if ! git reset --hard "$initial_changeset"; then
            error "Failed to perform hard reset to changeset: $initial_changeset. Manual intervention is required."
        fi
    fi

    if [[ $cleanup_maintenance_branch == 1 ]]; then
        info "Removing maintenance branch: $maintenance_branch"
        if ! git branch --delete --force "$cleanup_maintenance_branch"; then
            error "Failed to force removal of maintenance branch: $maintenance_branch. Manual intervention is required."
        fi
    fi

    if [[ $cleanup_tag == 1 ]]; then
        info "Removing tag: $version"
        if ! git tag --delete "$version"; then
            error "Failed to remove release tag: $version. Manual intervention is required."
        fi
    fi

    # Switch back to HEAD of current branch.
    if [[ -n $current_branch ]]; then
        git checkout --quiet "$current_branch"
    fi

    exit "$exit_code"
}

# Define error codes.
SUCCESS=0
ERROR_ARGUMENTS=1
ERROR_NOT_IMPLEMENTED=10
ERROR_INVALID_WORKING_DIRECTORY=11
ERROR_USER_ABORTED=12
ERROR_TESTS_FAILED=13
ERROR_VCS_FAILURE=14
ERROR_BUILD_FAILURE=15
ERROR_PYPI_FAILURE=16

# Disable debug mode by default.
debug=0

# Default URI to use for publishing to PyPI.
pypi_repository_url="https://upload.pypi.org/legacy/"

# Register our cleanup function, and request that no cleanup is
# performed by default.
cleanup_reset=0
cleanup_maintenance_branch=0
cleanup_tag=0
trap cleanup EXIT

# If no arguments were given, just show usage help.
if [[ -z $1 ]]; then
    short_usage
    exit "$SUCCESS"
fi

# Parse the arguments
while getopts "r:qdvh" opt; do
    case "$opt" in
        r) pypi_repository_url="$OPTARG";;
	d) debug=1;;
        v) version_and_licensing
           exit "$SUCCESS";;
        h) usage
           exit "$SUCCESS";;
        *) short_usage
           exit "$ERROR_ARGUMENTS";;
    esac
done
i=$OPTIND
shift $(($i-1))

# Read the positional arguments.
operation="$1"
version="$2"

# Verify positional arguments.
if [[ -z $operation || -z $version ]]; then
    error "Operation and version must be specified."
    exit "$ERROR_ARGUMENTS"
fi

if [[ $operation != "prepare" && $operation != "publish" ]]; then
    error "Invalid opertion specified: '$operation'"
    exit "$ERROR_ARGUMENTS"
fi

if [[ ! $version =~ ^([0-9]|[1-9][0-9]+)\.([0-9]|[1-9][0-9]+)\.([0-9]|[1-9][0-9]+)$ ]] ; then
    error "Invalid version string specified (must be MAJOR.MINOR.PATCH without leading zeros): $version"
    exit "$ERROR_ARGUMENTS"
fi

# Extract major, minor, and patch number from version.
major_number=$(echo "$version" | cut -d '.' -f 1)
minor_number=$(echo "$version" | cut -d '.' -f 2)
patch_number=$(echo "$version" | cut -d '.' -f 3)

# Set maintenance branch name.
maintenance_branch="maintenance/$major_number.$minor_number"

debug "Version: $version"
debug "Major number: $major_number"
debug "Minor number: $minor_number"
debug "Patch number: $patch_number"
debug "Maintenance branch: $maintenance_branch"

# Extract information about existing environment.
current_branch=$(git rev-parse --abbrev-ref HEAD)
initial_changeset=$(git rev-parse HEAD)
working_directory_status=$(git status -s)
available_tags=$(git tag | grep -E '^[[:digit:]]+\.[[:digit:]]+\.[[:digit:]]+$')

debug "Current branch: $current_branch"
debug "Initial changeset: $initial_changeset"
debug "Working directory status:\n${working_directory_status}"
debug "Available tags:\n$available_tags"

# Perform some basic verification of working directory etc.
if [[ -n $working_directory_status ]]; then
    error "Uncommitted or new files detected in working directory. Perform the following actions as necessary: \
commit/revert the changes, update the .gitignore file/remove untracked files."
    exit "$ERROR_INVALID_WORKING_DIRECTORY"
fi

if ! [[ $current_branch == "master" || $current_branch =~ ^maintenance/[[:digit:]]+\.[[:digit:]]+$ ]]; then
    error "Releases are supported only from the master and maintenance branches. Current branch: $current_branch"
    exit "$ERROR_INVALID_WORKING_DIRECTORY"
fi

if [[ $major_number == 0 && $minor_number == 0 ]]; then
    error "Cannot use zeros for both major and minor number in version."
    exit "$ERROR_ARGUMENTS"
fi

if [[ $operation == "prepare" ]]; then
    # Perform some basic sanity checks prior to proceeding.
    if git rev-parse --quiet --verify "$version" > /dev/null; then
        error "Requested version ($version) has already been tagged. Aborting the process."
        exit "$ERROR_ARGUMENTS"
    fi

    if [[ $current_branch == "master" && $patch_number != 0 ]]; then
        error "Only new major/minor (non-patch) releases are supported from the master branch."
        exit "$ERROR_ARGUMENTS"
    fi

    if [[ $current_branch == "master" ]] && git rev-parse --abbrev-ref "$maintenance_branch" >/dev/null 2>&1; then
        error "A new major/minor releases has been requested, but the maintenance branch is already present."
        exit "$ERROR_INVALID_WORKING_DIRECTORY"
    fi

    if [[ $current_branch != "master" ]] && [[ $patch_number == 0 ]]; then
        error "Only patch releases can be created from maintenance branches."
        exit "$ERROR_ARGUMENTS"
    fi

    if [[ $current_branch != "master" && $current_branch != "$maintenance_branch" ]]; then
        error "Patch releases must be created from matching maintenance branch."
        exit "$ERROR_ARGUMENTS"
    fi

    echo
    warning "Preparing local Git repository for release of version $version. New commits, tags, and maintenance branches will be created as necessary."
    echo

    read -p "Do you want to continue? (y/N) " confirm_release
    echo

    # Abort on user's request.
    if ! [[ $confirm_release == "y" || $confirm_release == "Y" ]]; then
        error "Aborting the preparation process as requested by user."
        exit "$ERROR_USER_ABORTED"
    fi

    # Initial test run prior to making changes.
    info "Running tests on current branch."
    if ! tox --recreate ; then
        error "Failed tests detected on current branch ($current_branch). Aborting the process."
        exit "$ERROR_TESTS_FAILED"
    fi

    # Request user's attention prior to making a signed commit and tag.
    warning "User interaction required for signing new commits and tag. Press [ENTER] to continue."
    read -s

    # Update version information for release.
    info "Updating release notes and package version."

    if ! { sed -i -E -e "/^NEXT RELEASE$/{N; s/.*/$version\n${version//?/-}/}" "docs/releasenotes.rst" && \
               sed -i -e "s/version='0.0.0'/version='$version'/" "setup.py"; }; then
        error "Failed to update version information. Aborting the process."
        cleanup_reset=1
        exit "$ERROR_VCS_FAILURE"
    fi

    # Commit updated version.
    info "Committing the version update."
    if ! { git add "docs/releasenotes.rst" "setup.py" && git commit --gpg-sign -m "Noticket: Preparing release $version."; }; then
        error "Failed to commit version update. Aborting the process."
        cleanup_reset=1
        exit "$ERROR_VCS_FAILURE"
    fi

    # Tag the version.
    info "Tagging the new release."
    if ! git tag --annotate --sign --message "Release $version." "$version"; then
        error "Failed to tag release. Aborting the process."
        cleanup_reset=1
        exit "$ERROR_VCS_FAILURE"
    fi

    # Rerun tests to ensure everything still works as expected.
    info "Running tests with new versioning information in place."
    if ! tox --recreate ; then
        error "Failed tests detected after updating versioning information. Aborting the process."
        cleanup_reset=1
        cleanup_tag=1
        exit "$ERROR_TESTS_FAILED"
    fi

    # Request user's attention prior to making a signed commit and tag.
    warning "User interaction required for starting new release notes and setting development package version. Press [ENTER] to continue."
    read -s

    # Updated release notes and package version for development.
    info "Adding new section to release notes for the next release, and switching package version to development."
    if ! { sed -i -E '/^=+/a \\n\nNEXT RELEASE\n------------' "docs/releasenotes.rst" && \
               sed -i -e "s/version='$version'/version='0.0.0'/" "setup.py"; }; then
        error "Failed to update version information. Aborting the process."
        cleanup_reset=1
        cleanup_tag=1
        exit "$ERROR_VCS_FAILURE"
    fi

    # Commit updated version.
    info "Committing the development version update."
    if ! { git add "docs/releasenotes.rst" "setup.py" && git commit --gpg-sign -m "Noticket: Switching to development version."; }; then
        error "Failed to commit development version update. Aborting the process."
        cleanup_reset=1
        cleanup_tag=1
        exit "$ERROR_VCS_FAILURE"
    fi

    # Create maintenance branch if necessary.
    if [[ $patch_number == 0 ]]; then
        info "Creating maintenance branch."
        if ! git branch "$maintenance_branch"; then
            error "Failed to create maintenance branch: $maintenance_branch"
            cleanup_reset=1
            cleanup_tag=1
            exit "$ERROR_VCS_FAILURE"
        fi
    fi
    success "Version $version has been successfully prepared for publishing in the local Git repository."
elif [[ $operation == "publish" ]]; then
    # Perform some basic sanity checks prior to proceeding.
    if ! git rev-parse --quiet --verify "$version" > /dev/null; then
        error "No such version ($version) has been tagged in the local repository. Please run the prepare operation first."
        exit "$ERROR_ARGUMENTS"
    fi

    echo
    warning "Publishing version $version. Relevant local branches and tag will be pushed to the origin, and package will be uploaded to PyPI. Prompts will be provided along the way to provide the necessary credentials."
    echo

    read -p "Do you want to continue? (y/N) " confirm_release
    echo

    # Abort on user's request.
    if ! [[ $confirm_release == "y" || $confirm_release == "Y" ]]; then
        error "Aborting the preparation process as requested by user."
        exit "$ERROR_USER_ABORTED"
    fi

    # Clean-up the local build directories.
    rm -rf dist/
    rm -rf build/

    # Checkout the release version.
    if ! git checkout --quiet "$version"; then
        error "Failed to checkout the designated release version."
        exit "$ERROR_VCS_FAILURE"
    fi

    if ! python setup.py sdist bdist_wheel; then
        error "Failed to build the source and binary distribution."
        exit "$ERROR_BUILD_FAILURE"
    fi

    if [[ $patch_number == 0 ]]; then
        info "Pushing the local master branch to origin."
        if ! git push origin master:master; then
            error "Failed to push the local master branch to the origin. Aborting the publishing process."
            exit "$ERROR_VCS_FAILURE"
        fi
    fi

    info "Pushing the local maintenance branch ($maintenance_branch) to origin."
    if ! git push origin "${maintenance_branch}:${maintenance_branch}"; then
        error "Failed to push the local maintenance branch to the origin. Aborting the publishing process."
        exit "$ERROR_VCS_FAILURE"
    fi

    info "Pushing the local tag ($version) to origin."
    if ! git push origin "$version"; then
        error "Failed to push the local tag to the origin. Aborting the publishing process."
        exit "$ERROR_VCS_FAILURE"
    fi

    info "Publishing the release to PyPI"
    if ! twine upload --repository-url "$pypi_repository_url" dist/*"$version"*; then
        error "Failed to publish the release to PyPI."
        exit "$ERROR_PYPI_FAILURE"
    fi

    success "Version $version has been successfully published to the origin Git repository and PyPI."
fi
