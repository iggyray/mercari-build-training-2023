import React, { useEffect, useState } from "react"

interface Item {
  id: number
  name: string
  category: string
  image_filename: string
}

const server = process.env.REACT_APP_API_URL || "http://127.0.0.1:9000"

interface Prop {
  reload?: boolean
  onLoadCompleted?: () => void
}

export const ItemList: React.FC<Prop> = (props) => {
  const { reload = true, onLoadCompleted } = props
  const [items, setItems] = useState<Item[]>([])
  const fetchItems = () => {
    fetch(server.concat("/items"), {
      method: "GET",
      mode: "cors",
      headers: {
        "Content-Type": "application/json",
        Accept: "application/json",
      },
    })
      .then((response) => response.json())
      .then((data) => {
        console.log("GET success:", data)
        setItems(data.items)
        onLoadCompleted && onLoadCompleted()
      })
      .catch((error) => {
        console.error("GET error:", error)
      })
  }

  useEffect(() => {
    if (reload) {
      fetchItems()
    }
  }, [reload])

  return (
    <div className="wrapper">
      {items.map((item) => {
        const itemId = item.id
        console.log(itemId)
        const imgSrc = `http://localhost:9000/image/${itemId}.jpg`
        console.log(imgSrc)
        return (
          <div key={item.id} className="ItemList">
            <img src={imgSrc} className="image" alt="item_image" />
            <p className="description">
              <p>Name: {item.name}</p>
              <p className="category">
                <small>Category: {item.category}</small>
              </p>
            </p>
          </div>
        )
      })}
    </div>
  )
}
