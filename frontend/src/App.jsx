import Sidebar from "./components/Sidebar";
import Navbar from "./components/Navbar";
import AppRoutes from "./routes/routes";

function App() {

    return (

        <div className="app">

            <Sidebar />

            <div className="main">

                <Navbar />

                <div className="content">

                    <AppRoutes />

                </div>

            </div>

        </div>

    );

}

export default App;