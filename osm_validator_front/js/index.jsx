import React from 'react';
import ReactDOM from 'react-dom';
import { Provider } from 'react-redux';
import configureStore from './store/configureStore.jsx';
import App from './containers/app.jsx';
import './../css/main.css';

const store = configureStore({
    user: undefined,
    loading: true
});

ReactDOM.render(
    <Provider store={store}>
        <App />
    </Provider>,
    document.getElementById('app')
);
