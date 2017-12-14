import {
    GET_USER_REQUEST,
    GET_USER_SUCCESS,
    GET_USER_ERROR
} from '../constants/user.jsx';

const initialState = {
    user: undefined,
    loading: false
};

// todo use { combineReducers } when redux v4.0.0 will be released
// now it's bug (https://github.com/reactjs/redux/releases)

export default function userstate(state = initialState, action) {
    switch (action.type) {
        case GET_USER_REQUEST:
            return Object.assign({}, state, { user: action.payload, loading: true });
        case GET_USER_SUCCESS:
            return Object.assign({}, state, { user: action.payload, loading: false });
        case GET_USER_ERROR:
            return Object.assign({}, state, { user: action.payload, loading: false });
        default:
            return state;
    }
}
