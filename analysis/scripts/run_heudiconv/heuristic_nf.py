def create_key(template, outtype=('nii.gz',), annotation_classes=None):
    return template, outtype, annotation_classes

def infotodict(seqinfo):
    keys = {
        't1': create_key('sub-{subject}/{session}/anat/sub-{subject}_{session}_T1w'),
        'fmap': create_key('sub-{subject}/{session}/fmap/sub-{subject}_{session}_dir-{dir}_run-{item:02d}_epi'),
        'rest': create_key('sub-{subject}/{session}/func/sub-{subject}_{session}_task-rest_run-{item:02d}_bold'),
        'restpre': create_key('sub-{subject}/{session}/func/sub-{subject}_{session}_task-restpre_run-{item:02d}_bold'),
        'restpost': create_key('sub-{subject}/{session}/func/sub-{subject}_{session}_task-restpost_run-{item:02d}_bold'),
        'transferpre': create_key('sub-{subject}/{session}/func/sub-{subject}_{session}_task-transferpre_run-{item:02d}_bold'),
        'transferpost': create_key('sub-{subject}/{session}/func/sub-{subject}_{session}_task-transferpost_run-{item:02d}_bold'),
        'feedback': create_key('sub-{subject}/{session}/func/sub-{subject}_{session}_task-feedback_run-{item:02d}_bold'),
    }

    info = {v: [] for v in keys.values()}

    for s in seqinfo:
        sd = s.series_description.lower()

        if 'localizer' in sd or 'scout' in sd or 'MoCo' in sd:
            continue
        elif 't1w' in sd:
        	info[keys['t1']].append(s.series_id)
        elif 'fmap' in sd and 'dir-ap' in sd:
            info[keys['fmap']].append({'dir': 'AP', 'item': s.series_id})
        elif 'fmap' in sd and 'dir-pa' in sd:
            info[keys['fmap']].append({'dir': 'PA', 'item': s.series_id})
        elif 'func_task_restpre' in sd:
            info[keys['restpre']].append(s.series_id)
        elif 'func_task_restpost' in sd:
            info[keys['restpost']].append(s.series_id)
        elif 'func_task_rest' in sd and 'restpost' not in sd and 'restpre' not in sd:
        	info[keys['rest']].append(s.series_id)
        elif 'transferpre' in sd:
            info[keys['transferpre']].append(s.series_id)
        elif 'transferpost' in sd:
            info[keys['transferpost']].append(s.series_id)
        elif 'feedback' in sd:
            info[keys['feedback']].append(s.series_id)

    return info

