import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'

const routes: RouteRecordRaw[] = [
  {
    path: '/',
    name: 'home',
    component: () => import('@/views/user/HomePage.vue'),
    meta: {
      title: '内容优化'
    }
  },
  {
    path: '/history',
    name: 'history',
    component: () => import('@/views/user/HistoryPage.vue'),
    meta: {
      title: '历史记录'
    }
  },
  {
    path: '/admin',
    name: 'admin',
    redirect: '/admin/login'
  },
  {
    path: '/admin/login',
    name: 'admin-login',
    component: () => import('@/views/admin/LoginPage.vue'),
    meta: {
      title: '管理员登录',
      hideNavbar: true
    }
  },
  {
    path: '/admin/dashboard',
    name: 'admin-dashboard',
    component: () => import('@/views/admin/DashboardPage.vue'),
    meta: {
      title: '管理后台',
      requiresAuth: true
    }
  },
  {
    path: '/admin/prohibited-words',
    name: 'admin-prohibited-words',
    component: () => import('@/views/admin/ProhibitedWordsPage.vue'),
    meta: {
      title: '违禁词管理',
      requiresAuth: true
    }
  },
  {
    path: '/admin/homophone-words',
    name: 'admin-homophone-words',
    component: () => import('@/views/admin/HomophoneWordsPage.vue'),
    meta: {
      title: '谐音词管理',
      requiresAuth: true
    }
  },
  {
    path: '/admin/users',
    name: 'admin-users',
    component: () => import('@/views/admin/AdminUsersPage.vue'),
    meta: {
      title: '账号管理',
      requiresAuth: true
    }
  },
  {
    path: '/admin/emojis',
    name: 'admin-emojis',
    component: () => import('@/views/admin/EmojiManagement.vue'),
    meta: {
      title: '表情管理',
      requiresAuth: true
    }
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'not-found',
    component: () => import('@/views/NotFoundPage.vue')
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 路由守卫
router.beforeEach((to, from, next) => {
  // 设置页面标题
  document.title = to.meta.title ? `${to.meta.title} - 小红书内容优化工具` : '小红书内容优化工具'
  
  // 检查管理员权限
  if (to.meta.requiresAuth) {
    const token = localStorage.getItem('admin_token')
    if (!token) {
      next('/admin/login')
      return
    }
  }
  
  next()
})

export default router