from coregraphene.ui import StyleSheet

SIDE = 2000

styles = StyleSheet({
    "container": {
        "name": "QWidget#main_block_widget",
        # "width": "100%",
        # "background-color": "rgb(220, 220, 255)",
    },
    "inactive_widget": {
        "name": "QWidget#inactive_widget",
        "width": f'{SIDE}px',
        "min-width": f'{SIDE}px',
        'height': f'{SIDE}px',
        'min-height': f'{SIDE}px',
        # 'opacity': '0.5',
        'background-color': "rgba(200, 200, 200, 0.2)",
    },
    "label_step_name": {
        # "height": "50px",
        # "min-width": f'300px',
        'background-color': "rgba(200, 200, 10, 0.8)",
        'font-size': "24px",
    }
})

# print(styles.container)
