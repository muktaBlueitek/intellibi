import { createSlice } from '@reduxjs/toolkit'
import { Dashboard } from '../../types/dashboard'

interface DashboardState {
  dashboards: Dashboard[]
  currentDashboard: Dashboard | null
  loading: boolean
  error: string | null
}

const initialState: DashboardState = {
  dashboards: [],
  currentDashboard: null,
  loading: false,
  error: null,
}

const dashboardSlice = createSlice({
  name: 'dashboard',
  initialState,
  reducers: {
    setDashboards: (state, action) => {
      state.dashboards = action.payload
    },
    setCurrentDashboard: (state, action) => {
      state.currentDashboard = action.payload
    },
    addDashboard: (state, action) => {
      state.dashboards.push(action.payload)
    },
    updateDashboard: (state, action) => {
      const index = state.dashboards.findIndex((d) => d.id === action.payload.id)
      if (index !== -1) {
        state.dashboards[index] = action.payload
      }
      if (state.currentDashboard?.id === action.payload.id) {
        state.currentDashboard = action.payload
      }
    },
    removeDashboard: (state, action) => {
      state.dashboards = state.dashboards.filter((d) => d.id !== action.payload)
      if (state.currentDashboard?.id === action.payload) {
        state.currentDashboard = null
      }
    },
    setLoading: (state, action) => {
      state.loading = action.payload
    },
    setError: (state, action) => {
      state.error = action.payload
    },
  },
})

export const {
  setDashboards,
  setCurrentDashboard,
  addDashboard,
  updateDashboard,
  removeDashboard,
  setLoading,
  setError,
} = dashboardSlice.actions
export default dashboardSlice.reducer
