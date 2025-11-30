// Community 기능을 위한 JavaScript
// 기존 chat.js의 스타일을 유지하면서 게시글/댓글 기능 추가

const API = {
    // 기존 API
    login: "/login",
    register: "/register",
    history: "/api/chat/history",
    send: "/api/chat/send",
    
    // 게시글 API
    getPosts: "/api/posts",
    getPost: (postId) => `/api/posts/${postId}`,
    createPost: "/api/posts/create",
    updatePost: "/api/posts/update",
    deletePost: (postId) => `/api/posts/delete/${postId}`,
    
    // 댓글 API
    createComment: "/api/comments/create",
    getComments: (postId) => `/api/comments/${postId}`,
    updateComment: "/api/comments/update",
    deleteComment: (commentId) => `/api/comments/delete/${commentId}`,
    
    // 좋아요 API
    toggleLike: "/api/likes/toggle",
    getLikeCount: (postId) => `/api/likes/${postId}`,
};

const state = {
    user: window.__AI_COMMUNITY_USER__ || null,
    theme: localStorage.getItem('theme') || 'dark',
    currentPosts: [],
};

// ===== Theme Management (기존 유지) =====
function initTheme() {
    document.documentElement.setAttribute('data-theme', state.theme);
    const themeToggle = document.getElementById('theme-toggle');
    if (themeToggle) {
        themeToggle.textContent = state.theme === 'dark' ? '☀️' : '🌙';
        themeToggle.addEventListener('click', toggleTheme);
    }
}

function toggleTheme() {
    state.theme = state.theme === 'dark' ? 'light' : 'dark';
    document.documentElement.setAttribute('data-theme', state.theme);
    localStorage.setItem('theme', state.theme);
    const themeToggle = document.getElementById('theme-toggle');
    if (themeToggle) {
        themeToggle.textContent = state.theme === 'dark' ? '☀️' : '🌙';
    }
    document.body.style.transition = 'all 0.5s ease';
    setTimeout(() => {
        document.body.style.transition = '';
    }, 500);
}

// ===== Particle Effect (최적화) =====
function createParticles() {
    const particlesContainer = document.createElement('div');
    particlesContainer.className = 'particles';
    document.body.appendChild(particlesContainer);
    
    // 파티클 개수 줄이기: 3초에 1개 → 6초에 1개
    setInterval(() => {
        const particle = document.createElement('div');
        particle.className = 'particle';
        particle.style.left = Math.random() * 100 + '%';
        particle.style.animationDuration = (Math.random() * 10 + 5) + 's';
        particle.style.animationDelay = Math.random() * 2 + 's';
        particlesContainer.appendChild(particle);
        
        setTimeout(() => {
            particle.remove();
        }, 15000);
    }, 6000); // 3000 → 6000으로 변경
}

// ===== Utility Functions =====
async function postJSON(url, payload) {
    const res = await fetch(url, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.message || "요청 실패");
    return data;
}

async function deleteJSON(url) {
    const res = await fetch(url, {
        method: "DELETE",
        headers: { "Content-Type": "application/json" },
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.message || "삭제 실패");
    return data;
}

async function putJSON(url, payload) {
    const res = await fetch(url, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.message || "수정 실패");
    return data;
}

function showNotification(message, isError = false) {
    const notification = document.createElement('div');
    notification.textContent = message;
    notification.style.cssText = `
        position: fixed;
        top: 100px;
        right: 20px;
        padding: 1rem 1.5rem;
        background: ${isError ? 'var(--error)' : 'var(--success)'};
        color: white;
        border-radius: var(--radius-md);
        box-shadow: var(--shadow-neon);
        z-index: 3000;
        animation: slideInRight 0.3s ease-out;
        font-weight: 600;
    `;
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.style.animation = 'fadeOut 0.3s ease-out';
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

// ===== Modal Functions =====
function openPostModal(postData = null) {
    const modal = document.getElementById('post-modal');
    const form = document.getElementById('post-form');
    const title = document.getElementById('post-title');
    const content = document.getElementById('post-content');
    const postId = document.getElementById('post-id');
    
    if (postData) {
        title.value = postData.title;
        content.value = postData.content;
        postId.value = postData.post_id;
        modal.querySelector('h2').textContent = '✏️ 게시글 수정';
    } else {
        form.reset();
        postId.value = '';
        modal.querySelector('h2').textContent = '✍️ 새 게시글 작성';
    }
    
    modal.style.display = 'flex';
}

function closePostModal() {
    const modal = document.getElementById('post-modal');
    modal.style.display = 'none';
}

// ===== Post Functions =====
function renderPost(post) {
    return `
        <article class="post-card" data-post-id="${post.post_id}">
            <div class="post-header">
                <div>
                    <h3 class="post-title">${escapeHtml(post.title)}</h3>
                    <div class="post-meta">
                        <span>👤 ${escapeHtml(post.author || '익명')}</span>
                        <span>📅 ${formatDate(post.created_at)}</span>
                        <span>❤️ ${post.like_count || 0}</span>
                        <span>💬 ${post.comment_count || 0}</span>
                    </div>
                </div>
            </div>
            <div class="post-content">${escapeHtml(post.content)}</div>
            <div class="post-actions">
                <button onclick="toggleLike(${post.post_id})" class="like-btn ${post.user_liked ? 'liked' : ''}">
                    ${post.user_liked ? '❤️' : '🤍'} 좋아요
                </button>
                <button onclick="toggleComments(${post.post_id})">
                    💬 댓글 보기
                </button>
                ${post.is_author ? `
                    <button onclick="editPost(${post.post_id})">✏️ 수정</button>
                    <button onclick="deletePost(${post.post_id})">🗑️ 삭제</button>
                ` : ''}
            </div>
            <div id="comments-${post.post_id}" class="comments-section" style="display: none;">
                <div class="comments-header">
                    <h4>💬 댓글 ${post.comment_count || 0}개</h4>
                </div>
                <div class="comments-list" id="comments-list-${post.post_id}"></div>
                <div class="comment-form">
                    <textarea placeholder="댓글을 입력하세요..." id="comment-input-${post.post_id}" rows="3"></textarea>
                    <button type="button" onclick="createComment(${post.post_id})">댓글 작성 ✈️</button>
                </div>
            </div>
        </article>
    `;
}

function renderComment(comment, postId) {
    const isAuthor = comment.user_id === state.user.id;
    return `
        <div class="comment" data-comment-id="${comment.comment_id}">
            <div class="comment-header">
                <span class="comment-author">${escapeHtml(comment.nickname || comment.user_id)}</span>
                <span class="comment-date">${formatDate(comment.created_at)}</span>
            </div>
            <div class="comment-body" id="comment-body-${comment.comment_id}">${escapeHtml(comment.comment_body)}</div>
            ${isAuthor ? `
                <div class="comment-actions">
                    <button onclick="editComment(${comment.comment_id}, ${postId})">✏️ 수정</button>
                    <button onclick="deleteComment(${comment.comment_id}, ${postId})">🗑️ 삭제</button>
                </div>
            ` : ''}
        </div>
    `;
}

async function loadPosts() {
    try {
        const res = await fetch(API.getPosts);
        const data = await res.json();
        
        if (data.status === 'SUCCESS' && data.posts) {
            state.currentPosts = data.posts;
            renderPosts(data.posts);
        } else {
            state.currentPosts = [];
            renderPosts([]);
        }
    } catch (error) {
        console.error('게시글 로드 실패:', error);
        showNotification('게시글을 불러오는데 실패했습니다.', true);
        state.currentPosts = [];
        renderPosts([]);
    }
}

function renderPosts(posts) {
    const container = document.getElementById('posts-container');
    if (!container) return;
    
    if (posts.length === 0) {
        container.innerHTML = `
            <div style="text-align: center; padding: 4rem; color: var(--text-muted);">
                <h2 style="color: var(--text-secondary); font-family: var(--font-display);">
                    📝 첫 게시글을 작성해보세요!
                </h2>
                <p>새 게시글 작성 버튼을 눌러 커뮤니티를 시작하세요.</p>
            </div>
        `;
        return;
    }
    
    container.innerHTML = posts.map(post => renderPost(post)).join('');
    
    // 댓글 입력창에 Enter 키 이벤트 추가
    posts.forEach(post => {
        const textarea = document.getElementById(`comment-input-${post.post_id}`);
        if (textarea) {
            textarea.addEventListener('keydown', (e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    createComment(post.post_id);
                }
            });
        }
    });
}

// ===== Comment Functions =====
async function toggleComments(postId) {
    const commentsSection = document.getElementById(`comments-${postId}`);
    
    if (commentsSection.style.display === 'none') {
        commentsSection.style.display = 'block';
        await loadComments(postId);
    } else {
        commentsSection.style.display = 'none';
    }
}

async function loadComments(postId) {
    try {
        const res = await fetch(API.getComments(postId));
        const data = await res.json();
        
        const commentsList = document.getElementById(`comments-list-${postId}`);
        if (!commentsList) return;
        
        if (data.status === 'SUCCESS') {
            if (data.comments && data.comments.length > 0) {
                commentsList.innerHTML = data.comments.map(c => renderComment(c, postId)).join('');
            } else {
                commentsList.innerHTML = '<p style="color: var(--text-muted); text-align: center; padding: 2rem;">아직 댓글이 없습니다. 첫 댓글을 작성해보세요! 💬</p>';
            }
        } else {
            commentsList.innerHTML = '<p style="color: var(--error); text-align: center; padding: 1rem;">댓글을 불러오는데 실패했습니다.</p>';
        }
    } catch (error) {
        console.error('댓글 로드 실패:', error);
        const commentsList = document.getElementById(`comments-list-${postId}`);
        if (commentsList) {
            commentsList.innerHTML = '<p style="color: var(--error); text-align: center; padding: 1rem;">댓글을 불러오는데 실패했습니다.</p>';
        }
    }
}

async function createComment(postId) {
    const input = document.getElementById(`comment-input-${postId}`);
    const commentBody = input.value.trim();
    
    if (!commentBody) {
        showNotification('댓글 내용을 입력해주세요.', true);
        return;
    }
    
    try {
        const result = await postJSON(API.createComment, {
            post_id: postId,
            comment_body: commentBody
        });
        
        if (result.status === 'SUCCESS') {
            showNotification('✅ 댓글이 작성되었습니다!');
            input.value = '';
            
            // 즉시 댓글 목록 새로고침
            await loadComments(postId);
            
            // 게시글 comment_count 업데이트
            const post = state.currentPosts.find(p => p.post_id === postId);
            if (post) {
                post.comment_count = (post.comment_count || 0) + 1;
                // 해당 게시글만 다시 렌더링
                const postCard = document.querySelector(`[data-post-id="${postId}"]`);
                if (postCard) {
                    const metaDiv = postCard.querySelector('.post-meta');
                    const commentCountSpan = Array.from(metaDiv.querySelectorAll('span')).find(
                        span => span.textContent.includes('💬')
                    );
                    if (commentCountSpan) {
                        commentCountSpan.textContent = `💬 ${post.comment_count}`;
                    }
                }
            }
        }
    } catch (error) {
        showNotification('❌ ' + error.message, true);
    }
}

async function editComment(commentId, postId) {
    const commentBody = document.getElementById(`comment-body-${commentId}`);
    const currentText = commentBody.textContent;
    const newText = prompt('댓글 수정:', currentText);
    
    if (newText && newText !== currentText) {
        try {
            const result = await putJSON(API.updateComment, {
                comment_id: commentId,
                comment_body: newText
            });
            
            if (result.status === 'SUCCESS') {
                showNotification('✅ 댓글이 수정되었습니다!');
                await loadComments(postId);
            }
        } catch (error) {
            showNotification('❌ ' + error.message, true);
        }
    }
}

async function deleteComment(commentId, postId) {
    if (!confirm('정말 이 댓글을 삭제하시겠습니까?')) return;
    
    try {
        const result = await deleteJSON(API.deleteComment(commentId));
        
        if (result.status === 'SUCCESS') {
            showNotification('✅ 댓글이 삭제되었습니다!');
            
            // 즉시 댓글 목록 새로고침
            await loadComments(postId);
            
            // 게시글 comment_count 업데이트
            const post = state.currentPosts.find(p => p.post_id === postId);
            if (post) {
                post.comment_count = Math.max(0, (post.comment_count || 0) - 1);
                // 해당 게시글만 다시 렌더링
                const postCard = document.querySelector(`[data-post-id="${postId}"]`);
                if (postCard) {
                    const metaDiv = postCard.querySelector('.post-meta');
                    const commentCountSpan = Array.from(metaDiv.querySelectorAll('span')).find(
                        span => span.textContent.includes('💬')
                    );
                    if (commentCountSpan) {
                        commentCountSpan.textContent = `💬 ${post.comment_count}`;
                    }
                }
            }
        }
    } catch (error) {
        showNotification('❌ ' + error.message, true);
    }
}

// ===== Helper Functions =====
function escapeHtml(text) {
    if (!text) return '';
    if (typeof text !== 'string') text = String(text);
    const map = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#039;'
    };
    return text.replace(/[&<>"']/g, m => map[m]);
}

function formatDate(dateString) {
    const date = new Date(dateString);
    const now = new Date();
    const diff = now - date;
    
    const minutes = Math.floor(diff / 60000);
    const hours = Math.floor(diff / 3600000);
    const days = Math.floor(diff / 86400000);
    
    if (minutes < 1) return '방금 전';
    if (minutes < 60) return `${minutes}분 전`;
    if (hours < 24) return `${hours}시간 전`;
    if (days < 7) return `${days}일 전`;
    
    return date.toLocaleDateString('ko-KR');
}

// ===== Event Listeners =====
function wireEventListeners() {
    // 새 게시글 작성 버튼
    const newPostBtn = document.getElementById('new-post-btn');
    if (newPostBtn) {
        newPostBtn.addEventListener('click', () => openPostModal());
    }
    
    // 게시글 새로고침 버튼
    const refreshBtn = document.getElementById('refresh-posts');
    if (refreshBtn) {
        refreshBtn.addEventListener('click', async () => {
            refreshBtn.textContent = '🔄 새로고침 중...';
            refreshBtn.disabled = true;
            await loadPosts();
            refreshBtn.textContent = '🔄 게시글 새로고침';
            refreshBtn.disabled = false;
        });
    }
    
    // 모달 닫기
    const closeBtn = document.querySelector('.modal-close');
    if (closeBtn) {
        closeBtn.addEventListener('click', closePostModal);
    }
    
    // 모달 배경 클릭 시 닫기
    const modal = document.getElementById('post-modal');
    if (modal) {
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                closePostModal();
            }
        });
    }
    
    // 게시글 폼 제출
    const postForm = document.getElementById('post-form');
    if (postForm) {
        postForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const formData = new FormData(postForm);
            const postData = {
                title: formData.get('title'),
                content: formData.get('content')
            };
            const postId = formData.get('post_id');
            
            try {
                let result;
                if (postId) {
                    // 수정
                    result = await putJSON(API.updatePost, { ...postData, post_id: postId });
                    showNotification('✅ 게시글이 수정되었습니다!');
                } else {
                    // 작성
                    result = await postJSON(API.createPost, postData);
                    showNotification('✅ 게시글이 작성되었습니다!');
                }
                
                closePostModal();
                await loadPosts();
            } catch (error) {
                showNotification('❌ ' + error.message, true);
            }
        });
    }
}

// ===== Initialization =====
document.addEventListener("DOMContentLoaded", () => {
    initTheme();
    createParticles();
    wireEventListeners();
    loadPosts();
    
    // 키보드 단축키
    document.addEventListener('keydown', (e) => {
        if (e.altKey && e.key === 't') {
            e.preventDefault();
            toggleTheme();
        }
    });
});

// ===== Global Functions (템플릿에서 호출) =====
window.openPostModal = openPostModal;
window.closePostModal = closePostModal;
window.toggleComments = toggleComments;
window.createComment = createComment;
window.editComment = editComment;
window.deleteComment = deleteComment;
window.toggleLike = async function(postId) {
    try {
        const result = await postJSON(API.toggleLike, { post_id: postId });
        if (result.status === 'SUCCESS') {
            showNotification(result.liked ? '❤️ 좋아요!' : '🤍 좋아요 취소');
            await loadPosts();
        }
    } catch (error) {
        showNotification('❌ ' + error.message, true);
    }
};
window.editPost = async function(postId) {
    const post = state.currentPosts.find(p => p.post_id === postId);
    if (post) {
        openPostModal(post);
    }
};
window.deletePost = async function(postId) {
    if (!confirm('정말 이 게시글을 삭제하시겠습니까?')) return;
    
    try {
        const result = await deleteJSON(API.deletePost(postId));
        if (result.status === 'SUCCESS') {
            showNotification('✅ 게시글이 삭제되었습니다!');
            await loadPosts();
        }
    } catch (error) {
        showNotification('❌ ' + error.message, true);
    }
};

