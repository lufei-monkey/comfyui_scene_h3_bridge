import json
import math

class SceneH3Slice:
    @classmethod
    def INPUT_TYPES(cls):
        return {'required': {'images': ('IMAGE',), 'scenes_json': ('STRING', {'forceInput': True}), 'scene_index': ('INT', {'default': 1, 'min': 1}), 'fps': ('FLOAT', {'default': 24., 'min': .01})}, 'optional': {'audio': ('AUDIO',)}}
    RETURN_TYPES = ('IMAGE', 'AUDIO', 'INT', 'FLOAT', 'STRING', 'STRING')
    RETURN_NAMES = ('frames', 'audio', 'frame_count', 'duration', 'filename_prefix', 'scene_info')
    FUNCTION = 'slice'
    CATEGORY = 'video/SceneDetect H3 Bridge'
    def slice(self, images, scenes_json, scene_index, fps, audio=None):
        data = json.loads(scenes_json)
        scenes = data['scenes']
        if not 1 <= scene_index <= len(scenes):
            raise ValueError(f'Scene index {scene_index} outside 1..{len(scenes)}')
        detected_fps = float(data['fps'])
        if not math.isclose(detected_fps, fps, rel_tol=0.001):
            raise ValueError('SceneDetect FPS and frame batch FPS differ; use the same source and FPS.')
        row = scenes[scene_index - 1]
        start, end = int(row['start_frame']), int(row['end_frame'])
        if not 0 <= start < end <= len(images):
            raise ValueError(f'Invalid scene range [{start}, {end}) for {len(images)} frames')
        cropped_audio = None
        if audio is not None:
            sr = int(audio['sample_rate'])
            waveform = audio['waveform']
            a, b = round(start / fps * sr), round(end / fps * sr)
            if a >= waveform.shape[-1]:
                raise ValueError('Audio ends before selected scene')
            cropped_audio = dict(audio, waveform=waveform[..., a:min(b, waveform.shape[-1])])
        info = dict(row, scene_index=scene_index, scene_count=len(scenes), local_start=0, local_duration=(end-start)/fps)
        return (images[start:end], cropped_audio, end-start, (end-start)/fps, f'H3_scene_{scene_index:03d}/replaced', json.dumps(info, ensure_ascii=False, indent=2))

NODE_CLASS_MAPPINGS = {'SceneH3Slice': SceneH3Slice}
NODE_DISPLAY_NAME_MAPPINGS = {'SceneH3Slice': 'SceneDetect → 完整镜头裁切（H3）'}
