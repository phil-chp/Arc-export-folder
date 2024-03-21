# Arc export folder

Hey friend! Are you looking for a way to export an Arc folder to Firefox? I hope I'm not the only crazy person that wanted this feature. I made it work as best as I could.

My reason for this is that I use Arc as my main browser, but I work on another computer that has Firefox, I desperately needed to be able to sync my important bookmarks on both of them, so here it is.

## How to use?

1. Clone this repository
2. Open Arc
3. Right click on the folder you want to export and click `Share Folder...` (Arc will generate a link that looks like this: `https://arc.net/folder/XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX`)
4. Run the script.

    ```
    python3 arc-export-folder.py https://arc.net/folder/XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX
    ```

5. After finishing you will get a `bookmarks.html` file, import it to Firefox. (By default bookmarks will land in the `Bookmarks Menu`)

### Icons?

Icons are pretty good brain candy, when you have a wall of bookmarks, they help navigate faster.

By default the script attempts it's best to fetch the website icon, though this does take some time, if you are in a rush just pass the `--no-icons` flag to skip this step.

## Q&A
<details>
<summary>...</summary>

### Does it work for other browsers?

Idk, but feel free to test. PR's are also welcome if you want to add support for other browsers!

### Why not just use the Arc shared folder page?

Did that, I have a lot of bookmarks, after having the page open for 5 min on firefox, it started to lag so much that Firefox complained about it being open.

And I prefer to have them in the bookmark menu, it's easier to access and navigate.

### Can I have the bookmarks in a specific folder?

No, this is a Firefox problem, and I feel like the import/export feature has not been updated since 1999, if you look at an actual export you will understand what I mean: `<!DOCTYPE NETSCAPE-Bookmark-file-1>` 💀 Come on Mozilla, get an intern on that...

</details>
