"""
视频分析的Celery任务模块。
"""
import logging
from celery import shared_task

from .services import VideoAnalysisService

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3)
def analyze_video_task(self, video_analysis_id: str):
    """
    在后台分析视频的Celery任务。
    
    参数:
        video_analysis_id: VideoAnalysis记录的UUID
    """
    try:
        logger.info(f"Starting video analysis for {video_analysis_id}")
        
        results = VideoAnalysisService.analyze_video(video_analysis_id)
        
        logger.info(f"Video analysis completed for {video_analysis_id}")
        return results
        
    except Exception as e:
        logger.error(f"Video analysis failed for {video_analysis_id}: {e}", exc_info=True)
        raise self.retry(exc=e, countdown=60)


@shared_task
def cleanup_old_videos(days: int = 90):
    """
    清理旧的视频文件。
    
    参数:
        days: 保留视频的天数
    """
    from datetime import timedelta
    from django.utils import timezone
    from .models import VideoAnalysis
    import os
    
    cutoff_date = timezone.now() - timedelta(days=days)
    
    old_analyses = VideoAnalysis.objects.filter(
        created_at__lt=cutoff_date,
        status='completed'
    )
    
    count = 0
    for analysis in old_analyses:
        if analysis.video_file:
            try:
                if os.path.isfile(analysis.video_file.path):
                    os.remove(analysis.video_file.path)
                count += 1
            except Exception as e:
                logger.error(f"Failed to delete video file: {e}")
    
    logger.info(f"Cleaned up {count} old video files")
    return count
