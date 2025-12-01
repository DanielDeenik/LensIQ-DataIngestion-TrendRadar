"""
Reddit Data Connector for LensIQ
Ingests unstructured data from Reddit for trend analysis
"""

import os
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import asyncio

try:
    import praw
    from praw.models import Submission, Comment
    PRAW_AVAILABLE = True
except ImportError:
    PRAW_AVAILABLE = False
    logging.warning("PRAW not installed. Reddit connector will use mock data.")

logger = logging.getLogger(__name__)


@dataclass
class RedditPost:
    """Structured Reddit post data."""
    post_id: str
    subreddit: str
    title: str
    content: str
    author: str
    created_utc: datetime
    score: int
    num_comments: int
    upvote_ratio: float
    url: str
    flair: Optional[str] = None
    is_self: bool = True
    permalink: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'post_id': self.post_id,
            'subreddit': self.subreddit,
            'title': self.title,
            'content': self.content,
            'author': self.author,
            'created_utc': self.created_utc.isoformat(),
            'score': self.score,
            'num_comments': self.num_comments,
            'upvote_ratio': self.upvote_ratio,
            'url': self.url,
            'flair': self.flair,
            'is_self': self.is_self,
            'permalink': self.permalink
        }


@dataclass
class RedditComment:
    """Structured Reddit comment data."""
    comment_id: str
    post_id: str
    subreddit: str
    content: str
    author: str
    created_utc: datetime
    score: int
    parent_id: str
    permalink: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'comment_id': self.comment_id,
            'post_id': self.post_id,
            'subreddit': self.subreddit,
            'content': self.content,
            'author': self.author,
            'created_utc': self.created_utc.isoformat(),
            'score': self.score,
            'parent_id': self.parent_id,
            'permalink': self.permalink
        }


class RedditConnector:
    """Connector for ingesting data from Reddit."""
    
    def __init__(self, 
                 client_id: Optional[str] = None,
                 client_secret: Optional[str] = None,
                 user_agent: Optional[str] = None):
        """
        Initialize Reddit connector.
        
        Args:
            client_id: Reddit API client ID
            client_secret: Reddit API client secret
            user_agent: User agent string
        """
        self.client_id = client_id or os.getenv('REDDIT_CLIENT_ID')
        self.client_secret = client_secret or os.getenv('REDDIT_CLIENT_SECRET')
        self.user_agent = user_agent or os.getenv('REDDIT_USER_AGENT', 'LensIQ/1.0')
        
        self.reddit = None
        if PRAW_AVAILABLE and self.client_id and self.client_secret:
            try:
                self.reddit = praw.Reddit(
                    client_id=self.client_id,
                    client_secret=self.client_secret,
                    user_agent=self.user_agent
                )
                logger.info("Reddit connector initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize Reddit connector: {e}")
                self.reddit = None
        else:
            logger.warning("Reddit connector using mock mode (no credentials)")
    
    def get_subreddit_posts(self,
                           subreddit_name: str,
                           limit: int = 100,
                           time_filter: str = 'week',
                           sort_by: str = 'hot') -> List[RedditPost]:
        """
        Get posts from a subreddit.
        
        Args:
            subreddit_name: Name of the subreddit
            limit: Maximum number of posts to retrieve
            time_filter: Time filter ('hour', 'day', 'week', 'month', 'year', 'all')
            sort_by: Sort method ('hot', 'new', 'top', 'rising')
            
        Returns:
            List of Reddit posts
        """
        if not self.reddit:
            return self._get_mock_posts(subreddit_name, limit)
        
        try:
            subreddit = self.reddit.subreddit(subreddit_name)
            posts = []
            
            # Get posts based on sort method
            if sort_by == 'hot':
                submissions = subreddit.hot(limit=limit)
            elif sort_by == 'new':
                submissions = subreddit.new(limit=limit)
            elif sort_by == 'top':
                submissions = subreddit.top(time_filter=time_filter, limit=limit)
            elif sort_by == 'rising':
                submissions = subreddit.rising(limit=limit)
            else:
                submissions = subreddit.hot(limit=limit)
            
            for submission in submissions:
                post = RedditPost(
                    post_id=submission.id,
                    subreddit=subreddit_name,
                    title=submission.title,
                    content=submission.selftext if submission.is_self else "",
                    author=str(submission.author) if submission.author else "[deleted]",
                    created_utc=datetime.fromtimestamp(submission.created_utc),
                    score=submission.score,
                    num_comments=submission.num_comments,
                    upvote_ratio=submission.upvote_ratio,
                    url=submission.url,
                    flair=submission.link_flair_text,
                    is_self=submission.is_self,
                    permalink=submission.permalink
                )
                posts.append(post)
            
            logger.info(f"Retrieved {len(posts)} posts from r/{subreddit_name}")
            return posts
            
        except Exception as e:
            logger.error(f"Error retrieving posts from r/{subreddit_name}: {e}")
            return self._get_mock_posts(subreddit_name, limit)
    
    def get_post_comments(self,
                         post_id: str,
                         limit: int = 100) -> List[RedditComment]:
        """
        Get comments from a specific post.
        
        Args:
            post_id: Reddit post ID
            limit: Maximum number of comments to retrieve
            
        Returns:
            List of Reddit comments
        """
        if not self.reddit:
            return self._get_mock_comments(post_id, limit)
        
        try:
            submission = self.reddit.submission(id=post_id)
            submission.comments.replace_more(limit=0)  # Remove "MoreComments" objects
            
            comments = []
            for comment in submission.comments.list()[:limit]:
                if isinstance(comment, Comment):
                    reddit_comment = RedditComment(
                        comment_id=comment.id,
                        post_id=post_id,
                        subreddit=str(submission.subreddit),
                        content=comment.body,
                        author=str(comment.author) if comment.author else "[deleted]",
                        created_utc=datetime.fromtimestamp(comment.created_utc),
                        score=comment.score,
                        parent_id=comment.parent_id,
                        permalink=comment.permalink
                    )
                    comments.append(reddit_comment)
            
            logger.info(f"Retrieved {len(comments)} comments from post {post_id}")
            return comments
            
        except Exception as e:
            logger.error(f"Error retrieving comments from post {post_id}: {e}")
            return self._get_mock_comments(post_id, limit)
    
    def search_subreddit(self,
                        subreddit_name: str,
                        query: str,
                        limit: int = 100,
                        time_filter: str = 'week') -> List[RedditPost]:
        """
        Search for posts in a subreddit.
        
        Args:
            subreddit_name: Name of the subreddit
            query: Search query
            limit: Maximum number of posts to retrieve
            time_filter: Time filter ('hour', 'day', 'week', 'month', 'year', 'all')
            
        Returns:
            List of Reddit posts matching the query
        """
        if not self.reddit:
            return self._get_mock_posts(subreddit_name, limit)
        
        try:
            subreddit = self.reddit.subreddit(subreddit_name)
            submissions = subreddit.search(query, time_filter=time_filter, limit=limit)
            
            posts = []
            for submission in submissions:
                post = RedditPost(
                    post_id=submission.id,
                    subreddit=subreddit_name,
                    title=submission.title,
                    content=submission.selftext if submission.is_self else "",
                    author=str(submission.author) if submission.author else "[deleted]",
                    created_utc=datetime.fromtimestamp(submission.created_utc),
                    score=submission.score,
                    num_comments=submission.num_comments,
                    upvote_ratio=submission.upvote_ratio,
                    url=submission.url,
                    flair=submission.link_flair_text,
                    is_self=submission.is_self,
                    permalink=submission.permalink
                )
                posts.append(post)
            
            logger.info(f"Found {len(posts)} posts matching '{query}' in r/{subreddit_name}")
            return posts
            
        except Exception as e:
            logger.error(f"Error searching r/{subreddit_name} for '{query}': {e}")
            return self._get_mock_posts(subreddit_name, limit)
    
    def _get_mock_posts(self, subreddit_name: str, limit: int) -> List[RedditPost]:
        """Generate mock Reddit posts for testing."""
        posts = []
        for i in range(min(limit, 10)):
            post = RedditPost(
                post_id=f"mock_{i}",
                subreddit=subreddit_name,
                title=f"Mock ESG Discussion {i+1}",
                content=f"This is mock content about sustainability and ESG trends. Post {i+1}.",
                author="mock_user",
                created_utc=datetime.now() - timedelta(days=i),
                score=100 - i*10,
                num_comments=50 - i*5,
                upvote_ratio=0.95 - i*0.01,
                url=f"https://reddit.com/r/{subreddit_name}/mock_{i}",
                flair="Discussion",
                is_self=True,
                permalink=f"/r/{subreddit_name}/comments/mock_{i}"
            )
            posts.append(post)
        return posts
    
    def _get_mock_comments(self, post_id: str, limit: int) -> List[RedditComment]:
        """Generate mock Reddit comments for testing."""
        comments = []
        for i in range(min(limit, 10)):
            comment = RedditComment(
                comment_id=f"mock_comment_{i}",
                post_id=post_id,
                subreddit="sustainability",
                content=f"Mock comment about ESG trends. Comment {i+1}.",
                author="mock_commenter",
                created_utc=datetime.now() - timedelta(hours=i),
                score=20 - i*2,
                parent_id=post_id if i == 0 else f"mock_comment_{i-1}",
                permalink=f"/r/sustainability/comments/{post_id}/mock_comment_{i}"
            )
            comments.append(comment)
        return comments


# Convenience function
def get_reddit_connector() -> RedditConnector:
    """Get Reddit connector instance."""
    return RedditConnector()

