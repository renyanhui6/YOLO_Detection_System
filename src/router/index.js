import Vue from 'vue'
import VueRouter from 'vue-router'
import Home from '@/views/Home.vue'
import ImageDetection from '@/views/ImageDetection.vue'
import VideoDetection from '@/views/VideoDetection.vue'
import DetectionHistory from '@/views/DetectionHistory.vue'
import IntelligentQA from '@/views/IntelligentQA.vue'
import KnowledgeBase from '@/views/KnowledgeBase.vue'
import ModelTraining from '@/views/ModelTraining.vue'

Vue.use(VueRouter)

const routes = [
  {
    path: '/',
    name: 'Home',
    component: Home
  },
  {
    path: '/image-detection',
    name: 'ImageDetection',
    component: ImageDetection
  },
  {
    path: '/video-detection',
    name: 'VideoDetection',
    component: VideoDetection
  },
  {
    path: '/detection-history',
    name: 'DetectionHistory',
    component: DetectionHistory
  },
  {
    path: '/intelligent-qa',
    name: 'IntelligentQA',
    component: IntelligentQA
  },
  {
    path: '/knowledge-base',
    name: 'KnowledgeBase',
    component: KnowledgeBase
  },
  {
    path: '/model-training',
    name: 'ModelTraining',
    component: ModelTraining
  }
]

const router = new VueRouter({
  mode: 'history',
  base: process.env.BASE_URL,
  routes
})

export default router
