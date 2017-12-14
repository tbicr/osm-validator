import axios from 'axios/index';
import {
    GET_USER_REQUEST,
    GET_USER_SUCCESS,
    GET_USER_ERROR
} from '../constants/user.jsx';

export function getUser() {
    return (dispatch) =>    {
        dispatch({
            type: GET_USER_REQUEST,
            payload: undefined
        });

        axios
            .get('/user/info')
            .then(function(result) {
                dispatch({
                    type: GET_USER_SUCCESS,
                    payload: result.data.osm_user
                })

            })
            .catch(function() {
                dispatch({
                    type: GET_USER_ERROR,
                    payload: undefined,
                    error: true
                })
            })
        ;
    }
}
