#!/bin/bash
#
# Provisioning script for the Vagrant test environment. Do not run
# outside of vagrant machine.
#

# Fail as soon as a command fails.
set -e

hostname=$(hostname)

if [[ $hostname != "gimmecert-testing" ]]; then
    echo "Script should only be run on Vagrant testing machine."
    exit 1
fi

# Update apt caches.
apt-get update -qq

# Install development tools.
apt-get install -qq -y git virtualenv

# Install Python build dependencies.
apt-get install -qq -y make build-essential libssl1.0-dev zlib1g-dev libbz2-dev libreadline-dev libsqlite3-dev wget curl llvm libncurses5-dev xz-utils tk-dev libxml2-dev libffi-dev

# Import public keys for validating Python releases.
sudo -i -u vagrant gpg -q --import /vagrant/provision/python_releases_signing_keys.pub

# Download and build additional Python versions.
python_versions=("3.4.9" "3.6.7" "3.7.1")
work_directory="/home/vagrant/src"

echo "Setting-up work directory."
sudo -i -u vagrant mkdir -p "$work_directory"

for version in "${python_versions[@]}"; do
    # Set-up information about Python version.
    minor_version="${version%.[[:digit:]]}"
    interpreter="/usr/local/bin/python${minor_version}"
    source_archive_link="https://www.python.org/ftp/python/${version}/Python-${version}.tar.xz"
    source_archive="$work_directory/Python-${version}.tar.xz"
    source_signature_link="https://www.python.org/ftp/python/${version}/Python-${version}.tar.xz.asc"
    source_signature="${source_archive}.asc"
    source="$work_directory/Python-${version}"

    # Check if the Python version has already been installed or not.
    if [[ ! -e $interpreter ]]; then
        echo
        echo
        echo "Installing Python $version"
        echo "=========================="

        echo "Downloading..."
        sudo -i -u vagrant wget -q -c -O "$source_archive" "$source_archive_link"
        sudo -i -u vagrant wget -q -c -O "$source_signature" "$source_signature_link"

        echo "Verifying signature..."
        sudo -i -u vagrant gpg --quiet --trust-model always --verify "$source_signature" "$source_archive"

        echo "Removing stale source files..."
        rm -rf "$source"

        echo "Unpacking source..."
        sudo -i -u vagrant tar xf "$source_archive" -C "$work_directory"

        echo "Configuring..."
        sudo -i -u vagrant <<< "cd ${source}; ./configure --quiet"

        echo "Building..."
        sudo -i -u vagrant make --quiet -C "$source" -j3

        echo "Installing..."
        make --quiet -C "$source" altinstall

        echo "Removing source files..."
        rm -rf "$source"
    fi
done

echo "Setting-up Python virtual environment for running tox."
if [[ ! -f /home/vagrant/virtualenv-tox/bin/activate ]]; then
    sudo -i -u vagrant virtualenv --prompt '(tox) ' -q -p /usr/bin/python3 /home/vagrant/virtualenv-tox
fi

echo "Setting-up Python virtual environment activation on login."
bash_profile="/home/vagrant/.bash_profile"
if [[ ! -e $bash_profile ]] || ! grep -q "source /home/vagrant/virtualenv-tox/bin/activate" "$bash_profile"; then
    echo 'source /home/vagrant/virtualenv-tox/bin/activate' >> "$bash_profile"
fi

echo "Cleaning-up Python byte-compiled files from repository directory."
sudo -i -u vagrant py3clean /vagrant/

echo "Installing development requirements."
sudo -i -u vagrant pip install -q -e "/vagrant[devel]"

echo
echo "SUCCESS: Ready for running tests."
