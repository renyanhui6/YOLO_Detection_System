let proxyObj = {}
// 知识库相关API代理到5002端口（数据库版）
proxyObj['/api/knowledge'] = {
  ws: false,
  target: 'http://localhost:5002',
  changeOrigin: true,
  pathRewrite:{
    '^/api/knowledge': '/api/knowledge'
  }
}
proxyObj['/api/categories'] = {
  ws: false,
  target: 'http://localhost:5002',
  changeOrigin: true,
  pathRewrite:{
    '^/api/categories': '/api/categories'
  }
}
proxyObj['/api/statistics'] = {
  ws: false,
  target: 'http://localhost:5002',
  changeOrigin: true,
  pathRewrite:{
    '^/api/statistics': '/api/statistics'
  }
}
proxyObj['/api/detection-results'] = {
  ws: false,
  target: 'http://localhost:3000',
  changeOrigin: true,
  pathRewrite:{
    '^/api/detection-results': '/api/detection-results'
  }
}
// 检测结果API代理到5002端口
proxyObj['/api/detection'] = {
  ws: false,
  target: 'http://localhost:5002',
  changeOrigin: true,
  pathRewrite:{
    '^/api/detection': '/api/detection'
  }
}
// YOLO检测API代理到YOLO服务器
proxyObj['/api/detect'] = {
  ws: false,
  target: 'http://localhost:5001',
  changeOrigin: true,
  pathRewrite:{
    '^/api/detect': '/api/detect'
  }
}
// // webSocket
// proxyObj['/ws'] = {
//   ws: true,
//   target: 'b3JpZ2luYWwgYXV0aG9y77yMYW5sdXhpIDIzNzUxODEwMDQ='
// }
module.exports = {
  lintOnSave: false,//是否开启eslint语法检查
  devServer: {
      host: 'localhost',
	  // 修改前端端口号
      port: 8080,
	  // 支持Vue Router的history模式
      historyApiFallback: true,
	  // 代理服务
      proxy: proxyObj
    }
}
