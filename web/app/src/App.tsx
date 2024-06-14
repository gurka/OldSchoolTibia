import { useLoaderData } from 'react-router-dom'
import { DataGrid, GridColDef } from '@mui/x-data-grid'
import { ExitToApp } from '@mui/icons-material';
import { Box } from '@mui/material';

const loader = async () => {
  return (await fetch("http://localhost:3000/recording")).json();
}

export default function App() {
  const recordings = useLoaderData() as Array<Recording>

  const format_ms = (ms: number) => {
    let res = ""
    if (ms >= (60 * 60 * 1000)) {
      res += `${Math.floor(ms / (60 * 60 * 1000))}h `
      ms %= (60 * 60 * 1000)
    }
    if (ms >= (60 * 1000)) {
      res += `${Math.floor(ms / (60 * 1000))}m `
      ms %= (60 * 1000)
    }
    if (ms >= 1000) {
      res += `${Math.floor(ms / 1000)}s`
    }
    return res;
  }

  const columns : GridColDef<Recording>[] = [
    { field: "filename", headerName: "filename", width: 400 },
    { field: "version", headerName: "version", width: 200, valueFormatter: (_, row) => row.version / 100 },
    { field: "length_ms", headerName: "length", width: 200, valueFormatter: (_, row) => format_ms(row.length_ms) },
  ]
  
  return (
    <Box  sx={{ height: 800, width: '100%' }}>
      <DataGrid
        rows={recordings}
        columns={columns}
        getRowId={(row) => row._id}
      />
    </Box>
  )
}

App.loader = loader

interface Recording {
  _id: string
  filename: string
  version: number
  length_ms: number
}

ExitToApp