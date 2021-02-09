#!/bin/bash
if [[ "$EUID" = 0 ]]; then
    echo "(1) already root"
else
    sudo -k # make sure to ask for password on next sudo
    if sudo true; then
        echo "(2) correct password"
    else
        echo "(3) wrong password"
        exit 1
    fi
fi
# currentDir="$( cd "$(realpath "$0" | sed 's|\(.*\)/.*|\1|' | sed 's|\(.*\)/.*|\1|')" >/dev/null 2>&1 ; pwd -P )"
# rulesPath="${currentDir}/resource/99-roboteq.rules"
sudo adduser $USER dialout
# sudo cp $rulesPath /etc/udev/rules.d/.
# sudo udevadm control --reload
