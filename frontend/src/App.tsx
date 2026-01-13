import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import MainLayout from './layouts/MainLayout'
import LoginPage from './pages/Login'
import DashboardPage from './pages/Dashboard'
import TaskListPage from './pages/tasks/TaskList'
import TaskDetailPage from './pages/tasks/TaskDetail'
import CreateTaskPage from './pages/tasks/CreateTask'
import EnvironmentListPage from './pages/environments/EnvironmentList'
import EnvironmentDetailPage from './pages/environments/EnvironmentDetail'
import TestSuiteListPage from './pages/test-suites/TestSuiteList'
import TestSuiteDetailPage from './pages/test-suites/TestSuiteDetail'
import ReportListPage from './pages/reports/ReportList'
import ReportDetailPage from './pages/reports/ReportDetail'
import ProjectListPage from './pages/projects/ProjectList'
import SettingsPage from './pages/Settings'
import { useAuthStore } from './stores/authStore'

function PrivateRoute({ children }: { children: React.ReactNode }) {
  const { isAuthenticated } = useAuthStore()
  
  if (!isAuthenticated) {
    return <Navigate to="/login" replace />
  }
  
  return <>{children}</>
}

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        <Route
          path="/"
          element={
            <PrivateRoute>
              <MainLayout />
            </PrivateRoute>
          }
        >
          <Route index element={<Navigate to="/dashboard" replace />} />
          <Route path="dashboard" element={<DashboardPage />} />
          
          {/* Tasks */}
          <Route path="tasks" element={<TaskListPage />} />
          <Route path="tasks/create" element={<CreateTaskPage />} />
          <Route path="tasks/:id" element={<TaskDetailPage />} />
          
          {/* Environments */}
          <Route path="environments" element={<EnvironmentListPage />} />
          <Route path="environments/:id" element={<EnvironmentDetailPage />} />
          
          {/* Test Suites */}
          <Route path="test-suites" element={<TestSuiteListPage />} />
          <Route path="test-suites/:id" element={<TestSuiteDetailPage />} />
          
          {/* Reports */}
          <Route path="reports" element={<ReportListPage />} />
          <Route path="reports/:id" element={<ReportDetailPage />} />
          
          {/* Projects */}
          <Route path="projects" element={<ProjectListPage />} />
          
          {/* Settings */}
          <Route path="settings" element={<SettingsPage />} />
        </Route>
      </Routes>
    </BrowserRouter>
  )
}

export default App
