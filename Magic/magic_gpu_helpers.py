import numpy as np

def process_batch(grids_np, args_dict):
    from magic_gpu import evaluate_grid_batch
    mask, _, score_detail = evaluate_grid_batch(grids_np, np,
        triangle_harmony=args_dict['triangle_harmony'],
        triangle_tol=args_dict['triangle_tol'],
        return_details=True,
        mode=args_dict['mode']
    )
    return mask, score_detail, grids_np
