import { BrowserRouter, Routes, Route } from "react-router-dom";
import Home from "./pages/Home";
import StandingTable from "./pages/Table";

function App() {
    return (
        <>
            <BrowserRouter>
                <Routes>
                    <Route index element={<Home />} />
                    <Route path="/home" element={<Home />} />
                    <Route
                        path="/premier-league/teams"
                        element={<StandingTable />}
                    />
                    <Route path="*" element={<h1>404 Not Found</h1>} />
                </Routes>
            </BrowserRouter>
        </>
    );
}

export default App;
