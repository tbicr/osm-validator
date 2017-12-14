import React from 'react';
import { Route, Switch } from 'react-router-dom';
import MainPage from './mainpage.jsx';
import SettingsPage from './settingspage.jsx';

export default class Content extends React.Component {
    render() {
        return (
            <Switch>
                <Route exact path='/' component={MainPage} />
                <Route path='/settings' component={SettingsPage} />
            </Switch>
        );
    }
}
