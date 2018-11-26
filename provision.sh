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

# Clone the pyenv and pyenv-virtualenv tools for setting-up multiple
# Python installations.
if [[ ! -e /home/vagrant/.pyenv ]]; then
    sudo -i -u vagrant git clone https://github.com/pyenv/pyenv/ /home/vagrant/.pyenv
fi

if [[ ! -e /home/vagrant/.pyenv/plugins/pyenv-virtualenv ]]; then
    sudo -i -u vagrant git clone https://github.com/pyenv/pyenv-virtualenv.git /home/vagrant/.pyenv/plugins/pyenv-virtualenv
fi

# Enable pyenv for the user.
bash_profile="/home/vagrant/.bash_profile"

if [[ ! -e $bash_profile ]] || ! grep -q "export PYENV_ROOT" "$bash_profile"; then
    echo 'export PYENV_ROOT="$HOME/.pyenv"' >> "$bash_profile"
fi

if [[ ! -e $bash_profile ]] || ! grep -q "export PATH=" "$bash_profile"; then
    echo 'export PATH="$PYENV_ROOT/bin:$PATH"' >> "$bash_profile"
fi

if [[ ! -e $bash_profile ]] || ! grep -q 'pyenv init' "$bash_profile"; then
    echo 'eval "$(pyenv init -)"' >> "$bash_profile"
fi

chown vagrant:vagrant "$bash_profile"
chmod 0640 "$bash_profile"

# List of Python versions to install.
python_versions=("3.4.9" "3.5.6" "3.6.7" "3.7.1")

# Install various Python versions.
for python_version in "${python_versions[@]}"; do
    sudo -i -u vagrant pyenv install -s "$python_version"
done

# Register them globally.
sudo -i -u vagrant pyenv global system "${python_versions[@]}"

# Set-up virtual environment for running tox.
if [[ ! -f /home/vagrant/virtualenv-tox/bin/activate ]]; then
    sudo -i -u vagrant virtualenv --prompt '(tox) ' -q -p /usr/bin/python3 /home/vagrant/virtualenv-tox
fi

if [[ ! -e $bash_profile ]] || ! grep -q "source /home/vagrant/virtualenv-tox/bin/activate" "$bash_profile"; then
    echo 'source /home/vagrant/virtualenv-tox/bin/activate' >> "$bash_profile"
fi

# Install development requirements.
sudo -i -u vagrant pip install -q -e "/vagrant[devel]"
