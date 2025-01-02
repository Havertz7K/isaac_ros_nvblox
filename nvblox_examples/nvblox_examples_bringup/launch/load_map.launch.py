from isaac_ros_launch_utils.all_types import *
import isaac_ros_launch_utils as lu

from nvblox_ros_python_utils.nvblox_launch_utils import NvbloxMode
from nvblox_ros_python_utils.nvblox_constants import NVBLOX_CONTAINER_NAME

def generate_launch_description() -> LaunchDescription:
    args = lu.ArgumentContainer()
    args.add_arg('log_level', 'info', choices=['debug', 'info', 'warn'], cli=True)
    args.add_arg('mode', NvbloxMode.static, choices=NvbloxMode.names(), cli=True)
    
    actions = args.get_launch_actions()

    # Set use_sim_time to false since we're just loading a map
    actions.append(SetParameter('use_sim_time', False))

    # Container
    actions.append(
        lu.component_container(
            NVBLOX_CONTAINER_NAME, 
            container_type='isolated', 
            log_level=args.log_level
        )
    )

    # Nvblox node with minimal configuration
    nvblox_node = ComposableNode(
        name='nvblox_node',
        package='nvblox_ros',
        plugin='nvblox::NvbloxNode',
        parameters=[
            # Load base config
            lu.get_path('nvblox_examples_bringup', 'config/nvblox/nvblox_base.yaml'),
            # Override some parameters
            {
                'use_depth': False,
                'use_color': False,
                'use_lidar': False,
                'mapping_type': 'static_tsdf',
                'esdf_mode': "3d",
                'publish_esdf_distance_slice': True,
                'publish_layer_pointcloud_rate_hz': 5.0,
                'update_mesh_rate_hz': 5.0,
                'update_esdf_rate_hz': 5.0,
            }
        ]
    )
    

    # Load the nvblox node
    actions.append(lu.load_composable_nodes(NVBLOX_CONTAINER_NAME, [nvblox_node]))

    # Add RViz
    rviz_config = lu.get_path('nvblox_examples_bringup', 'config/visualization/map.rviz')
    actions.append(
        Node(
            package='rviz2',
            executable='rviz2',
            name='rviz2',
            arguments=['-d', str(rviz_config)],
            output='screen'
        )
    )

    return LaunchDescription(actions)