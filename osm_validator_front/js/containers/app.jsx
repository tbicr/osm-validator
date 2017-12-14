import React from 'react';
import { bindActionCreators } from 'redux';
import Content from '../components/content.jsx';
import MainMenu from '../components/mainmenu.jsx';
import Login from '../components/login.jsx';
import { connect } from 'react-redux';
import * as pageActions from '../actions/pageactions.jsx';
import { HashRouter, hashHistory } from 'react-router-dom';

class App extends React.Component {
    componentDidMount() {
        this.props.pageActions.getUser();
    }

    render() {
        if (this.props.loading && !this.props.user) {
            return (
                <div>Loading...</div>
            );
        } else if (this.props.user) {
            return (
                <HashRouter history={hashHistory}>
                    <div className='container'>
                        <div className='row'>
                            <MainMenu />
                        </div>
                        <Content />
                    </div>
                </HashRouter>
            );
        } else {
            return (
                <Login />
            );
        }
    }
}

function mapStateToProps (state) {
    return {
        user: state.user,
        loading: state.loading
    };
}

function mapDispatchToProps(dispatch) {
    return {
        pageActions: bindActionCreators(pageActions, dispatch)
    };
}

export default connect(mapStateToProps, mapDispatchToProps)(App);
