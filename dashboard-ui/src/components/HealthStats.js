import React, { useEffect, useState } from 'react'
import '../App.css';

export default function AppStats() {
    const [isLoaded, setIsLoaded] = useState(false);
    const [stats, setStats] = useState({});
    const [error, setError] = useState(null)

	const getStats = () => {
	
        fetch(`http://aceit3855.westus.cloudapp.azure.com:8120/health`)
            .then(res => res.json())
            .then((result)=>{
				console.log("Received Stats")
                setStats(result);
                setIsLoaded(true);
            },(error) =>{
                setError(error)
                setIsLoaded(true);
            })
    }
    useEffect(() => {
		const interval = setInterval(() => getStats(), 10000); // Update every 10 seconds
		return() => clearInterval(interval);
    }, [getStats]);

    if (error){
        console.log(error)
        console.log("hi")
        return (<div className={"error"}>Error found when fetching from API</div>)
    } else if (isLoaded === false){
        return(<div>Loading...</div>)
    } else if (isLoaded === true){
        return(
            <div>
                <table className={"StatsTable"}>
					<tbody>
						<tr>
							<th>Service Health: </th>
						</tr>
						<tr>
							<td colspan="2">Receiver: {stats['receiver']}</td>
						</tr>
						<tr>
							<td colspan="2">Storage: {stats['storage']}</td>
						</tr>
						<tr>
							<td colspan="2">Processing: {stats['processing']}</td>
						</tr>
						<tr>
							<td colspan="2">Audit: {stats['audit']}</td>
						</tr>
					</tbody>
                </table>
                <h4>Last Updated: {stats['last_update']}</h4>

            </div>
        )
    }
}