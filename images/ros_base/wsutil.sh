#!/bin/bash

# Strict env settings
# http://tldp.org/LDP/abs/html/options.html
# Abort script at first error, when a command exits with non-zero status
# (except in until or while loops, if-tests, list constructs)
set -e
# Attempt to use undefined variable outputs error message, and forces an exit
set -u
# Causes a pipeline to return the exit status of the last command in the pipe
# that returned a non-zero return value.
set -o pipefail
# Print each command to stdout before executing it
# set -v

_echo () {
    echo "[wsutil.sh] ${@}"
}

launch_help () {
    echo "Catkin workspace helper script supporting typical dev workflows."
    echo ""
    echo "Arguments:"
    echo ""
    echo "-h --help Show this text."
    echo "--init Initialize workspace."
    echo "--setup_subpath If initializing workspace, use this subpath in the"
    echo "                workspace as the setup call to source in bash."
    echo "                Defaults to: ${setup_subpath}"
    echo "--add_to_entrypoint Add workspace to entrypoint script."
    echo "--rosdep Run rosdep and get dependencies via apt."
    echo "--rosdep_args Arguments to pass to rosdep. Defaults to \"\"."
    echo "--catkin_make Build workspace with catkin_make_isolated."
    echo "--catkin_make_args Arguments to pass to catkin_make_isolated"
    echo "                   Defaults to \"--use-ninja -j32 -l32\"."
    echo "--build_workflow Get dependencies and build:"
    echo "      rosdep"
    echo "      catkin_make"
    echo "workspaces The workspace names (not path) to process."
    echo ""
}

mydir="$(dirname "$(realpath -s $0)")"

# Arg defaults
run_help=false
run_init=false
setup_subpath="devel_isolated/setup.bash"
run_add_to_entrypoint=false
run_rosdep=false
rosdep_args=""
run_catkin_make=false
catkin_make_args="--use-ninja -j16 -l16"
workspaces=()

_echo "Reading cmd line args:"
for arg_raw in "$@"; do
    _echo "ARG: ${arg_raw}"
    arg_key="${arg_raw%%=*}"
    arg_val="${arg_raw#*=}"
    case $arg_raw in
        -h|--help)
            _echo "    help enabled"
            run_help=true
            ;;
        --init)
            _echo "    init enabled (also runs add_to_entrypoint)"
            run_init=true
            run_add_to_entrypoint=true
            ;;
        --setup_subpath=?*)
            setup_subpath="${arg_val}"
            _echo "    setup_subpath set to ${setup_subpath}"
            ;;
        --add_to_entrypoint)
            _echo "    add_to_entrypoint"
            run_add_to_entrypoint=true
            ;;
        --rosdep)
            _echo "    rosdep enabled"
            run_rosdep=true
            ;;
        --rosdep_args=?*)
            rosdep_args="${arg_val}"
            _echo "    rosdep_args set to ${rosdep_args}"
            ;;
        --catkin_make)
            _echo "    cakin_make enabled"
            run_catkin_make=true
            ;;
        --catkin_make_args=?*)
            catkin_make_args="${arg_val}"
            _echo "    catkin_make_args set to ${catkin_make_args}"
            ;;
        --build_workflow)
            _echo "    build_workflow enabled"
            run_rosdep=true
            run_catkin_make=true
            ;;
        # All other style args cause an error
        -?*)
            _echo "ERROR: Unknown cmd line arg: ${arg_raw}"
            exit 1
            ;;
        # Non flags are the workspace(s) to process
        *)
            if [[ "${arg_raw}" = /* ]]; then
                # absolute path
                this_ws="${arg_raw}"
            else
                # relative path
                this_ws="$(readlink -f ${arg_raw})"
            fi
            if [ -z "${this_ws}" ]; then
                _echo "ERROR: workspace cannot be resolved: ${arg_raw}"
                exit 1
            fi
            if [ "${run_add_to_entrypoint}" = false ] && [ ! -d $this_ws ]; then
                _echo "ERROR: cannot find ws: ${this_ws}"
                exit 1
            fi
            _echo "    ws added: ${this_ws}"
            workspaces+=$this_ws
            ;;
    esac
    shift
done

# Launch help and exit
if [ "${run_help}" = true ]; then
    launch_help
    exit 0
fi

if [ ${#workspaces[@]} -eq 0 ]; then
    _echo "ERROR: No workspaces passed. See --help:"
    _echo ""
    launch_help
    exit 1
fi

check_for_ros_pkgs () {
    local ws=$1
    local src=$ws/src
    local num_cmake=$(find "${src}" -name "CMakeLists.txt" | wc -l)
    local num_pkg=$(find "${src}" -name "package.xml" | wc -l)
    if [[ $num_cmake -gt 0 ]] && \
       [[ $num_pkg -gt 0 ]]; then
        _echo "Found ${num_pkg} ROS packages in here: ${ws}"
    else
        _echo "ERROR: No ROS packages in here: ${ws}. Exitting!"
        exit 1
    fi
}

for ws in "${workspaces[@]}"; do

    _echo "Processing ws: ${ws}"

    if [ "$run_init" = true ]; then
        _echo "Running init"
        mkdir -p $ws/src
    fi

    if [ "$run_add_to_entrypoint" = true ]; then
        _echo "Running add_to_entrypoint"
        # Add source to entrypoint above final exec statement
        _path="${ws}/${setup_subpath}"
        _line="if [ -f ${_path} ]; then source ${_path}; else echo \"WARNING: No file to source: ${_path}\"; fi"
        _echo "Adding \"${_line}\" to /entrypoint.sh"
        sed -i "/^exec/i ${_line}" /entrypoint.sh
    fi

    if [ "$run_rosdep" = true ]; then
        _echo "Running rosdep"
        cd $ws
        check_for_ros_pkgs $ws
        apt-get update
        rosdep update
        set +u
        rosdep install --from-paths src --ignore-src --rosdistro $ROS_DISTRO --as-root=apt:false -y ${rosdep_args}
        set -u
        rm -rf /var/lib/apt/lists/
        apt-get clean
    fi

    if [ "$run_catkin_make" = true ]; then
        _echo "Running catkin_make"
        cd $ws
        check_for_ros_pkgs $ws
        set +u
        source /entrypoint.sh
        set -u
        catkin_make_isolated ${catkin_make_args}
    fi

done
