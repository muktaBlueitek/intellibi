import { createSlice } from '@reduxjs/toolkit'
import { DataSource } from '../../types/datasource'

interface DataSourceState {
  datasources: DataSource[]
  currentDataSource: DataSource | null
  loading: boolean
  error: string | null
}

const initialState: DataSourceState = {
  datasources: [],
  currentDataSource: null,
  loading: false,
  error: null,
}

const datasourceSlice = createSlice({
  name: 'datasource',
  initialState,
  reducers: {
    setDataSources: (state, action) => {
      state.datasources = action.payload
    },
    setCurrentDataSource: (state, action) => {
      state.currentDataSource = action.payload
    },
    addDataSource: (state, action) => {
      state.datasources.push(action.payload)
    },
    updateDataSource: (state, action) => {
      const index = state.datasources.findIndex((d) => d.id === action.payload.id)
      if (index !== -1) {
        state.datasources[index] = action.payload
      }
    },
    removeDataSource: (state, action) => {
      state.datasources = state.datasources.filter((d) => d.id !== action.payload)
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
  setDataSources,
  setCurrentDataSource,
  addDataSource,
  updateDataSource,
  removeDataSource,
  setLoading,
  setError,
} = datasourceSlice.actions
export default datasourceSlice.reducer
