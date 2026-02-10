import { createSlice, createAsyncThunk } from '@reduxjs/toolkit'
import { userService } from '../../services/api/userService'
import { User } from '../../types/user'

interface UserState {
  currentUser: User | null
  loading: boolean
  error: string | null
}

const initialState: UserState = {
  currentUser: null,
  loading: false,
  error: null,
}

export const fetchCurrentUser = createAsyncThunk(
  'user/fetchCurrentUser',
  async (_, { rejectWithValue }) => {
    try {
      const user = await userService.getCurrentUser()
      return user
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || 'Failed to fetch user')
    }
  }
)

const userSlice = createSlice({
  name: 'user',
  initialState,
  reducers: {
    clearUser: (state) => {
      state.currentUser = null
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchCurrentUser.pending, (state) => {
        state.loading = true
        state.error = null
      })
      .addCase(fetchCurrentUser.fulfilled, (state, action) => {
        state.loading = false
        state.currentUser = action.payload
        state.error = null
      })
      .addCase(fetchCurrentUser.rejected, (state, action) => {
        state.loading = false
        state.error = action.payload as string
      })
  },
})

export const { clearUser } = userSlice.actions
export default userSlice.reducer
