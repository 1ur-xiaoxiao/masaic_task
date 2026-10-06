"""检查裁剪块对齐、颜色匹配和无效素材处理，不需要运行多进程。"""
import importlib.util
from pathlib import Path
import tempfile
import unittest

from PIL import Image

SCRIPT = Path(__file__).resolve().parents[1] / '1.py'
spec = importlib.util.spec_from_file_location('mosaic_task', SCRIPT)
mosaic_task = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mosaic_task)


class MosaicTests(unittest.TestCase):
    def test_cropped_target_blocks_stay_aligned(self):
        # 203*8=1624，裁到1600；匹配图应为160宽，而不是原来的162宽。
        with tempfile.TemporaryDirectory() as directory:
            image_path = Path(directory) / 'target.png'
            Image.new('RGB', (203, 157), 'yellow').save(image_path)
            large, small = mosaic_task.TargetImage(image_path).get_data()
        self.assertEqual(large.size, (1600, 1250))
        self.assertEqual(small.size, (160, 125))
        self.assertEqual(large.width // mosaic_task.TILE_SIZE, small.width // mosaic_task.TILE_MATCH_RES)

    def test_closest_color_is_selected(self):
        fitter = mosaic_task.TileFitter([[(255, 0, 0)], [(0, 255, 0)], [(0, 0, 255)]])
        self.assertEqual(fitter.get_best_fit_tile([(10, 240, 10)]), 1)

    def test_unreadable_tile_does_not_discard_valid_tile(self):
        with tempfile.TemporaryDirectory() as directory:
            Image.new('RGB', (80, 60), 'blue').save(Path(directory) / 'valid.jpg')
            (Path(directory) / 'broken.jpg').write_text('not an image', encoding='utf-8')
            large, small = mosaic_task.TileProcessor(directory).get_tiles()
        self.assertEqual(len(large), 1)
        self.assertEqual(large[0].size, (50, 50))
        self.assertEqual(small[0].size, (5, 5))


if __name__ == '__main__':
    unittest.main()
