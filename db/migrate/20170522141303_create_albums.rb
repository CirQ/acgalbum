class CreateAlbums < ActiveRecord::Migration[5.0]
  def change
    create_table :albums do |t|
      t.string :name
      t.string :site
      t.string :description
      t.string :coverpath
      t.bigint :fingerprint
      t.references :artist, foreign_key: true
    end
  end
end
