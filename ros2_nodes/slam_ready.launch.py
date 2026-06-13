from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        
        # NODE 1: Visual Odometry (With Anti-Freeze Coasting, IMU Disabled)
        Node(
            package='rtabmap_odom', 
            executable='rgbd_odometry', 
            name='rgbd_odometry',
            parameters=[{
                'frame_id': 'oak-d-base-frame', 
                'approx_sync': True,
                
                # --- THE ANTI-FREEZE HACKS ---
                'Odom/ResetCountdown': '0',    # Coast using constant velocity when blind
                'Odom/GuessMotion': 'true',    # Guess the next position if the camera blurs
            }],
            remappings=[
                ('rgb/image', '/oak/rgb/image_raw'),
                ('depth/image', '/oak/stereo/image_raw'),
                ('rgb/camera_info', '/oak/rgb/camera_info')
            ],
            output='screen'
        ),
        
        # NODE 2: RTAB-Map SLAM Engine
        Node(
            package='rtabmap_slam', 
            executable='rtabmap', 
            name='rtabmap',
            parameters=[{
                'frame_id': 'oak-d-base-frame', 
                'subscribe_depth': True, 
                'subscribe_rgb': True, 
                'subscribe_odom': True,
            }],
            remappings=[
                ('rgb/image', '/oak/rgb/image_raw'),
                ('depth/image', '/oak/stereo/image_raw'),
                ('rgb/camera_info', '/oak/rgb/camera_info'),
                ('odom', '/odom')
            ],
            output='screen'
        )
    ])
