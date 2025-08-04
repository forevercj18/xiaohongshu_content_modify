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
  // 管理界面路由 - 独立访问
  {
    path: '/management',
    name: 'management',
    redirect: '/management/login'
  },
  {
    path: '/management/login',
    name: 'management-login',
    component: () => import('@/views/admin/LoginPage.vue'),
    meta: {
      title: '管理员登录',
      hideNavbar: true,
      isManagement: true
    }
  },
  {
    path: '/management/dashboard',
    name: 'management-dashboard',
    component: () => import('@/views/admin/DashboardPage.vue'),
    meta: {
      title: '管理后台',
      requiresAuth: true,
      isManagement: true
    }
  },
  {
    path: '/management/prohibited-words',
    name: 'management-prohibited-words',
    component: () => import('@/views/admin/ProhibitedWordsPage.vue'),
    meta: {
      title: '违禁词管理',
      requiresAuth: true,
      isManagement: true
    }
  },
  {
    path: '/management/homophone-words',
    name: 'management-homophone-words',
    component: () => import('@/views/admin/HomophoneWordsPage.vue'),
    meta: {
      title: '谐音词管理',
      requiresAuth: true,
      isManagement: true
    }
  },
  {
    path: '/management/users',
    name: 'management-users',
    component: () => import('@/views/admin/AdminUsersPage.vue'),
    meta: {
      title: '账号管理',
      requiresAuth: true,
      isManagement: true
    }
  },
  {
    path: '/management/emojis',
    name: 'management-emojis',
    component: () => import('@/views/admin/EmojiManagement.vue'),
    meta: {
      title: '表情管理',
      requiresAuth: true,
      isManagement: true
    }
  },
  {
    path: '/management/whitelist',
    name: 'management-whitelist',
    component: () => import('@/views/admin/WhitelistManagement.vue'),
    meta: {
      title: '白名单管理',
      requiresAuth: true,
      isManagement: true
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
  if (to.meta.isManagement) {
    document.title = to.meta.title ? `${to.meta.title} - 管理后台` : '管理后台'
  } else {
    document.title = to.meta.title ? `${to.meta.title} - 小红书内容优化工具` : '小红书内容优化工具'
  }
  
  // 检查管理员权限（仅对管理路由）
  if (to.meta.requiresAuth && to.meta.isManagement) {
    const token = localStorage.getItem('admin_token')
    if (!token) {
      next('/management/login')
      return
    }
  }
  
  next()
})

export default router